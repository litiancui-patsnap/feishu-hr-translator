import json
from datetime import datetime

from fastapi.testclient import TestClient

from src.ai.qwen import DummyQwenClient
from src.config import Settings
from src.main import create_app
from src.okr.source import build_okr_source
from src.schemas import HRExtract, NeedItem, OKRAlignment, ReportIn, RiskItem
from src.storage.csv_store import CSVStorage
from src.storage.base import StorageDriver


class MemoryStorage(StorageDriver):
    def __init__(self) -> None:
        self.records = []

    async def save(self, record) -> None:
        self.records.append(record)


def _build_extract() -> HRExtract:
    return HRExtract(
        hr_summary="完成支付接口灰度，风险可控。",
        risks=[RiskItem(item="支付延迟", likelihood="medium", mitigation="扩容网关")],
        needs=[NeedItem(topic="业务协作", owner="HRBP")],
        okr_alignment=OKRAlignment(
            hit_objectives=["O1"],
            hit_krs=["KR1"],
            gaps=[],
            confidence=0.6,
        ),
        next_actions=["跟进测试数据"],
        risk_level="medium",
    )


def test_end_to_end_webhook(tmp_path, monkeypatch):
    monkeypatch.setenv("FEISHU_BOT_VERIFICATION_TOKEN", "secret")
    csv_path = tmp_path / "reports.csv"
    okr_cache_path = tmp_path / "okr.json"
    okr_cache_path.write_text(
        json.dumps(
            {
                "users": [
                    {
                        "user_id": "u_123",
                        "objectives": [
                            {
                                "id": "O1",
                                "title": "提升产品稳定性",
                                "period_start": "2024-01-01",
                                "period_end": "2024-12-31",
                                "krs": [
                                    {
                                        "id": "KR1",
                                        "title": "接口错误率低于0.1%",
                                        "progress": "40%",
                                    }
                                ],
                            }
                        ],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    settings = Settings(
        app_port=8000,
        base_url="http://test",
        feishu_bot_verification_token="secret",
        storage_driver="csv",
        csv_path=str(csv_path),
        okr_source="cache",
        okr_cache_path=str(okr_cache_path),
    )
    storage = CSVStorage(str(csv_path))
    okr_source = build_okr_source(settings)
    qwen = DummyQwenClient(_build_extract())

    app = create_app(
        settings=settings,
        storage=storage,
        qwen_client=qwen,
        okr_source=okr_source,
    )
    client = TestClient(app)

    payload = {
        "schema": "2.0",
        "header": {"event_id": "abc", "token": "secret"},
        "event": {
            "message": {
                "message_id": "m1",
                "message_type": "text",
                "content": json.dumps({"text": "本周周报：完成支付接口灰度"}),
                "create_time": str(int(datetime.now().timestamp() * 1000)),
                "sender": {"user_id": "u_123", "name": "张三"},
            }
        },
    }

    response = client.post("/webhook/feishu", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] is True

    rows = csv_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(rows) == 2
    assert "张三" in rows[1]


def test_simple_payload_normalization(tmp_path, monkeypatch):
    monkeypatch.delenv("FEISHU_BOT_VERIFICATION_TOKEN", raising=False)
    csv_path = tmp_path / "reports.csv"
    okr_cache_path = tmp_path / "okr.json"
    okr_cache_path.write_text(
        json.dumps({"users": []}),
        encoding="utf-8",
    )
    settings = Settings(
        app_port=8000,
        base_url="http://test",
        feishu_bot_verification_token="",
        storage_driver="csv",
        csv_path=str(csv_path),
        okr_source="cache",
        okr_cache_path=str(okr_cache_path),
        dashscope_api_key="fake",
    )
    storage = CSVStorage(str(csv_path))
    okr_source = build_okr_source(settings)
    qwen = DummyQwenClient(_build_extract())

    app = create_app(
        settings=settings,
        storage=storage,
        qwen_client=qwen,
        okr_source=okr_source,
    )
    client = TestClient(app)

    payload = {
        "user_id": "u_123",
        "user_name": "airbang",
        "text": "[Weekly] finished canary release of payment API.",
    }
    response = client.post("/webhook/feishu", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] is True
