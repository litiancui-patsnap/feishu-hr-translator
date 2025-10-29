from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException, status

from ..ai.qwen import QwenClient
from ..config import Settings
from ..okr.source import OKRSource
from ..schemas import FeishuWebhookEnvelope, ReportIn, StoredReport
from ..storage.base import StorageDriver
from ..utils.logger import get_logger
from ..utils.period import detect_period
from .api_client import FeishuAPIClient
from .cards import build_summary_card

logger = get_logger(__name__)


class FeishuWebhookHandler:
    def __init__(
        self,
        settings: Settings,
        qwen_client: QwenClient,
        storage: StorageDriver,
        okr_source: OKRSource,
        feishu_client: FeishuAPIClient,
    ) -> None:
        self.settings = settings
        self.qwen_client = qwen_client
        self.storage = storage
        self.okr_source = okr_source
        self.feishu_client = feishu_client

    async def handle(
        self, payload: Dict[str, Any] | FeishuWebhookEnvelope, *, validate_token: bool = True
    ) -> Dict[str, Any]:
        if isinstance(payload, FeishuWebhookEnvelope):
            envelope = payload
        else:
            envelope = FeishuWebhookEnvelope.model_validate(payload)
        if validate_token:
            self._validate_token(envelope)
        message = envelope.event.message
        text = self._extract_text(message.message_type, message.content)
        message_ts = _parse_timestamp(message.create_time)
        period_type, period_start, period_end = detect_period(text, message_ts.date())
        report = ReportIn(
            user_id=message.sender.preferred_user_id,
            user_name=message.sender.name or message.sender.preferred_user_id,
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            raw_text=text,
            message_ts=message_ts,
        )
        okr_brief = await self.okr_source.get_okr_brief(
            report.user_id, period_start, period_end
        )
        extract = await self.qwen_client.generate_hr_extract(report, okr_brief)
        card = build_summary_card(report, extract)
        record = StoredReport(report=report, hr_extract=extract, okr_brief=okr_brief)
        await self.storage.save(record)
        await self.feishu_client.send_card(card)
        logger.info(
            "webhook_processed",
            extra={
                "user_id": report.user_id,
                "period_type": report.period_type,
                "okr_brief_len": len(okr_brief),
            },
        )
        return {"ok": True}

    def _validate_token(self, envelope: FeishuWebhookEnvelope) -> None:
        expected = self.settings.feishu_bot_verification_token
        if not expected:
            logger.warning("verification_token_not_configured")
            return
        incoming = envelope.header.token
        if incoming != expected:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid verification token",
            )

    def _extract_text(self, message_type: str, content: str) -> str:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return content
        if message_type == "text" and "text" in payload:
            return payload["text"]
        if message_type == "post":
            # Rich text payload: flatten simple content fields.
            return _flatten_rich_text(payload)
        return json.dumps(payload, ensure_ascii=False)


def _parse_timestamp(value: str) -> datetime:
    if len(value) > 10:
        return datetime.fromtimestamp(int(value) / 1000)
    return datetime.fromtimestamp(int(value))


def _flatten_rich_text(payload: Dict[str, Any]) -> str:
    content = payload.get("content", [])
    parts = []
    for blocks in content:
        if not isinstance(blocks, list):
            continue
        for item in blocks:
            text = item.get("text")
            if text:
                parts.append(text)
    return "\n".join(parts)
