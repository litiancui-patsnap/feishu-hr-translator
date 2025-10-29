from __future__ import annotations

import asyncio
import time
import json
from typing import Any, Dict, Optional

import httpx

from ..utils.logger import get_logger

logger = get_logger(__name__)

TENANT_TOKEN_URL = (
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
)
SEND_MESSAGE_URL = (
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
)


class FeishuAPIClient:
    def __init__(
        self,
        app_id: Optional[str],
        app_secret: Optional[str],
        default_chat_id: Optional[str],
        timeout: float = 10.0,
        trust_env: bool = False,
    ) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.default_chat_id = default_chat_id
        self.timeout = timeout
        self.trust_env = trust_env
        self._tenant_token: Optional[str] = None
        self._tenant_token_expiry: float = 0.0
        self._lock = asyncio.Lock()

    async def send_card(self, card_payload: Dict[str, Any], chat_id: Optional[str] = None) -> None:
        target_chat = chat_id or self.default_chat_id
        if not target_chat:
            logger.info(
                "feishu_card_preview",
                extra={"card_payload": card_payload},
            )
            return
        token = await self._get_tenant_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        body = {
            "receive_id": target_chat,
            "msg_type": "interactive",
            "content": json.dumps(card_payload, ensure_ascii=False),
        }
        async with httpx.AsyncClient(
            timeout=self.timeout, trust_env=self.trust_env
        ) as client:
            response = await client.post(SEND_MESSAGE_URL, headers=headers, json=body)
            if response.status_code in {429, 500, 502, 503}:
                logger.error(
                    "feishu_send_retryable",
                    extra={"status_code": response.status_code, "body": response.text},
                )
                response.raise_for_status()
            response.raise_for_status()
        logger.info(
            "feishu_card_sent",
            extra={"chat_id": target_chat, "status": "success"},
        )

    async def _get_tenant_token(self) -> str:
        async with self._lock:
            if self._tenant_token and time.time() < self._tenant_token_expiry:
                return self._tenant_token
            if not self.app_id or not self.app_secret:
                raise RuntimeError("Feishu app credentials are required to send cards.")
            payload = {"app_id": self.app_id, "app_secret": self.app_secret}
            async with httpx.AsyncClient(
                timeout=self.timeout, trust_env=self.trust_env
            ) as client:
                response = await client.post(TENANT_TOKEN_URL, json=payload)
                response.raise_for_status()
                data = response.json()
            if data.get("code") != 0:
                raise RuntimeError(f"Failed to retrieve tenant token: {data}")
            self._tenant_token = data["tenant_access_token"]
            expire = int(data.get("expire", 600))
            self._tenant_token_expiry = time.time() + expire - 60
            logger.info("feishu_token_refreshed", extra={"expires_in": expire})
            return self._tenant_token
