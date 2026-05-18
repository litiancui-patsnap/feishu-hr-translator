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


def test_rendered_prompt_requires_faithful_boss_friendly_summary():
    now = datetime.utcnow()
    report = ReportIn(
        user_id="u_1",
        user_name="李田翠",
        period_type="weekly",
        period_start=now.date(),
        period_end=now.date(),
        raw_text=(
            "本周主要完成了 guanzhao-ip-agent V1 验收闭环和交底交接能力的收尾工作。\n"
            "项目在 V1 可交付性上进一步增强：主流程可以通过脚本跑通；"
            "Compose 环境更稳定；登录 / CORS 问题已修复；交底导出链路更完整；"
            "审核后附件边界更安全；本地和 CI 验证均通过。\n"
            "下周工作计划：梳理 V1 已完成能力和后续功能缺口，围绕当前 main 分支继续整理："
            "仍是 fixture / provider placeholder 的部分；前端页面中还不够业务化的展示；"
            "后台任务、审计、导出相关的缺口；与 AGENTS.md、ROADMAP、V2_PRODUCT_DESIGN.md 的差距。"
        ),
        message_ts=now,
    )
    qwen = QwenClient(api_key="test", model="qwen-test")

    system_prompt, user_prompt = qwen._render_prompts(report, "O1：AI辅助养老系统可交付")

    assert "不做战略扩写" in system_prompt
    assert "只能使用【报告文本】和【该人员OKR】中明确出现的信息" in user_prompt
    assert "不得凭经验添加“多平台适配、复杂工单处理、客户反馈”" in user_prompt
    assert "fixture/provider placeholder" in user_prompt
    assert "交底导出链路更完整" in user_prompt


def test_rendered_prompt_keeps_daily_report_narrow():
    now = datetime.utcnow()
    report = ReportIn(
        user_id="u_2",
        user_name="张三",
        period_type="daily",
        period_start=now.date(),
        period_end=now.date(),
        raw_text="今日修复登录 / CORS 问题，明日继续补充导出校验。",
        message_ts=now,
    )
    qwen = QwenClient(api_key="test", model="qwen-test")

    _, user_prompt = qwen._render_prompts(report, "O1：提升系统可交付质量")

    assert "对于日报，输出应更短" in user_prompt
    assert "不要把单日进展扩写成阶段性成果、长期目标或团队级结论" in user_prompt
    assert "今日修复登录 / CORS 问题" in user_prompt
    assert "明日继续补充导出校验" in user_prompt


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
