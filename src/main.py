from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status

from .ai.qwen import QwenClient
from .config import Settings, get_settings
from .feishu.api_client import FeishuAPIClient
from .feishu.webhook import FeishuWebhookHandler
from .okr.source import OKRSource, build_okr_source
from .schemas import FeishuWebhookEnvelope
from .storage import build_storage
from .storage.base import StorageDriver
from .utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


def create_app(
    settings: Optional[Settings] = None,
    storage: Optional[StorageDriver] = None,
    qwen_client: Optional[QwenClient] = None,
    okr_source: Optional[OKRSource] = None,
    feishu_client: Optional[FeishuAPIClient] = None,
) -> FastAPI:
    setup_logging()
    settings = settings or get_settings()
    storage = storage or build_storage(settings)
    okr_source = okr_source or build_okr_source(settings)
    qwen_client = qwen_client or QwenClient(
        api_key=settings.dashscope_api_key,
        model=settings.qwen_model,
        timeout=settings.request_timeout,
        api_mode=settings.qwen_api_mode,
        trust_env=settings.http_trust_env,
    )
    feishu_client = feishu_client or FeishuAPIClient(
        app_id=settings.feishu_app_id,
        app_secret=settings.feishu_app_secret,
        default_chat_id=settings.feishu_default_chat_id,
        timeout=settings.request_timeout,
        trust_env=settings.http_trust_env,
    )
    handler = FeishuWebhookHandler(
        settings=settings,
        qwen_client=qwen_client,
        storage=storage,
        okr_source=okr_source,
        feishu_client=feishu_client,
    )

    app = FastAPI(title="Feishu HR Translator")

    @app.get("/healthz")
    async def healthz() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/webhook/feishu")
    async def feishu_webhook(request: Request) -> dict[str, bool]:
        raw_body = await request.body()
        try:
            payload_data = json.loads(raw_body.decode("utf-8"))
        except UnicodeDecodeError:
            payload_data = json.loads(raw_body.decode("utf-8", errors="ignore"))
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON payload: {exc}",
            ) from exc
        payload = _normalize_webhook_payload(payload_data, settings)
        if payload.get("type") == "url_verification" and "challenge" in payload:
            return {"challenge": payload["challenge"]}

        envelope = FeishuWebhookEnvelope.model_validate(payload)
        _validate_webhook_token(envelope, settings)

        async def _process_webhook() -> None:
            try:
                await handler.handle(envelope, validate_token=False)
            except Exception:
                logger.exception(
                    "webhook_processing_failed",
                    extra={"event_id": envelope.header.event_id},
                )

        asyncio.create_task(_process_webhook())
        return {"ok": True}

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("app_startup", extra={"storage_driver": settings.storage_driver})

    return app


app = create_app()


def _validate_webhook_token(
    envelope: FeishuWebhookEnvelope, settings: Settings
) -> None:
    expected = settings.feishu_bot_verification_token
    if not expected:
        logger.warning("verification_token_not_configured")
        return
    incoming = envelope.header.token
    if incoming != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification token",
        )


def _normalize_webhook_payload(
    payload: Dict[str, Any], settings: Settings
) -> Dict[str, Any]:
    if "event" in payload and isinstance(payload["event"], dict):
        return payload

    if {"user_id", "user_name", "text"} <= payload.keys():
        now_ms = int(datetime.utcnow().timestamp() * 1000)
        message = {
            "message_id": payload.get("message_id", "demo-message"),
            "message_type": "text",
            "content": json.dumps({"text": payload["text"]}, ensure_ascii=False),
            "create_time": str(now_ms),
            "sender": {
                "user_id": payload["user_id"],
                "name": payload.get("user_name", payload["user_id"]),
            },
        }
        token = settings.feishu_bot_verification_token or payload.get("token", "")
        return {
            "schema": "2.0",
            "header": {
                "event_id": payload.get("event_id", "demo-event"),
                "token": token,
            },
            "event": {"message": message},
        }

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported payload format for Feishu webhook.",
    )
