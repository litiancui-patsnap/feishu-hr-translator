import json
from datetime import datetime

import httpx
import pytest

from src.ai.qwen import QwenClient
from src.schemas import HRExtract, ReportIn


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _hr_extract_payload() -> dict:
    return {
        "hr_summary": "总结",
        "risks": [
            {"item": "延迟", "likelihood": "medium", "mitigation": "增加人手"}
        ],
        "needs": [{"topic": "支持成本", "owner": "HR"}],
        "okr_alignment": {
            "hit_objectives": ["O1"],
            "hit_krs": ["KR1"],
            "gaps": [],
            "confidence": 0.8,
        },
        "next_actions": ["跟进客户反馈"],
        "risk_level": "medium",
    }


def _mock_transport(responses):
    responses = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        if not responses:
            raise AssertionError("No more responses configured")
        response = responses.pop(0)
        return response

    return httpx.MockTransport(handler)


def _sample_report() -> ReportIn:
    now = datetime.utcnow()
    return ReportIn(
        user_id="u_1",
        user_name="测试",
        period_type="daily",
        period_start=now.date(),
        period_end=now.date(),
        raw_text="日报内容",
        message_ts=now,
    )


@pytest.mark.anyio("asyncio")
async def test_qwen_parses_valid_response():
    payload = {"output": {"text": json.dumps(_hr_extract_payload(), ensure_ascii=False)}}
    transport = _mock_transport([httpx.Response(status_code=200, json=payload)])
    client = httpx.AsyncClient(transport=transport)
    qwen = QwenClient(api_key="test", model="qwen-test", http_client=client)

    result = await qwen.generate_hr_extract(_sample_report(), "OKR")
    assert isinstance(result, HRExtract)
    await client.aclose()


@pytest.mark.anyio("asyncio")
async def test_qwen_retries_on_invalid_json():
    bad_payload = {"output": {"text": "not-json"}}
    good_payload = {"output": {"text": json.dumps(_hr_extract_payload())}}
    transport = _mock_transport(
        [
            httpx.Response(status_code=200, json=bad_payload),
            httpx.Response(status_code=200, json=good_payload),
        ]
    )
    client = httpx.AsyncClient(transport=transport)
    qwen = QwenClient(api_key="test", model="qwen-test", http_client=client)

    report = _sample_report()
    result = await qwen.generate_hr_extract(report, "OKR")
    assert result.okr_alignment.hit_krs == ["KR1"]
    await client.aclose()


@pytest.mark.anyio("asyncio")
async def test_qwen_fallback_on_timeout():
    def raise_timeout(request: httpx.Request) -> httpx.Response:  # pragma: no cover - signature required
        raise httpx.ReadTimeout("timeout")

    transport = httpx.MockTransport(raise_timeout)
    client = httpx.AsyncClient(transport=transport)
    qwen = QwenClient(api_key="test", model="qwen-test", http_client=client, max_retries=1)

    result = await qwen.generate_hr_extract(_sample_report(), "OKR")
    assert result.hr_summary.startswith("(离线模式)")
    assert result.okr_alignment.confidence == pytest.approx(0.1)
    await client.aclose()


@pytest.mark.anyio("asyncio")
async def test_qwen_compatible_mode():
    payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(_hr_extract_payload(), ensure_ascii=False)
                }
            }
        ]
    }
    transport = _mock_transport([httpx.Response(status_code=200, json=payload)])
    client = httpx.AsyncClient(transport=transport)
    qwen = QwenClient(
        api_key="test",
        model="qwen-plus",
        http_client=client,
        api_mode="compatible",
    )

    result = await qwen.generate_hr_extract(_sample_report(), "OKR")
    assert result.hr_summary == "总结"
    await client.aclose()
