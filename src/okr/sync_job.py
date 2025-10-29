from __future__ import annotations

import asyncio
import calendar
import json
import re
from datetime import date
from pathlib import Path
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Iterable, List, Set

import httpx

from ..config import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
OKR_BATCH_GET_URL = "https://open.feishu.cn/open-apis/okr/v1/okrs/batch_get"


async def fetch_tenant_access_token(app_id: str, app_secret: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            TOKEN_URL,
            json={"app_id": app_id, "app_secret": app_secret},
        )
        response.raise_for_status()
        payload = response.json()
    if payload.get("code") != 0:
        raise RuntimeError(f"Failed to fetch tenant token: {payload}")
    return payload["tenant_access_token"]


def chunked(sequence: List[str], size: int) -> Iterable[List[str]]:
    for index in range(0, len(sequence), size):
        yield sequence[index : index + size]


def _infer_period(name: str) -> tuple[date, date]:
    """Attempt to infer a monthly window from the OKR name."""
    match = re.search(r"(\d{4}).*?(\d{1,2})", name)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
    else:
        today = date.today()
        year, month = today.year, today.month
    start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)
    return start, end


def _extract_owner_id(objective: Dict[str, Any]) -> str | None:
    owner_fields = objective.get("owner") or {}
    for key in ("user_id", "open_id", "union_id"):
        value = owner_fields.get(key)
        if value:
            return value
    candidates = objective.get("aligning_objective_list") or []
    for item in candidates:
        owner = item.get("owner") or {}
        for key in ("user_id", "open_id", "union_id"):
            value = owner.get(key)
            if value:
                return value
    return None


def _collect_owner_ids(okr: Dict[str, Any]) -> List[str]:
    result: Set[str] = set()
    owner = okr.get("owner") or {}
    for key in ("user_id", "open_id", "union_id"):
        value = owner.get(key)
        if value:
            result.add(value)
            break
    for node in okr.get("owner_list", []) or []:
        for key in ("user_id", "open_id", "union_id"):
            value = node.get(key)
            if value:
                result.add(value)
                break
    return list(result)


def _parse_overrides(raw: str | None) -> Dict[str, str]:
    overrides: Dict[str, str] = {}
    if not raw:
        return overrides
    for item in raw.split(";"):
        item = item.strip()
        if not item or ":" not in item:
            continue
        okr_id, user_id = item.split(":", 1)
        okr_id = okr_id.strip()
        user_id = user_id.strip()
        if okr_id and user_id:
            overrides[okr_id] = user_id
    return overrides


def _normalise_okrs(
    okrs: List[Dict[str, Any]], overrides: Dict[str, str]
) -> Dict[str, Any]:
    users: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
    for okr in okrs:
        period_start, period_end = _infer_period(okr.get("name", ""))
        okr_owner_ids = _collect_owner_ids(okr)
        for objective in okr.get("objective_list", []):
            owner_id = _extract_owner_id(objective)
            target_owner_ids = [owner_id] if owner_id else okr_owner_ids
            if not target_owner_ids:
                override_user = overrides.get(okr.get("id", ""))
                if override_user:
                    target_owner_ids = [override_user]
                else:
                    logger.warning(
                        "okr_owner_missing",
                        extra={
                            "okr_id": okr.get("id"),
                            "objective_id": objective.get("id"),
                            "owner": objective.get("owner"),
                            "owner_list": okr.get("owner_list"),
                            "aligning_objective_list": objective.get(
                                "aligning_objective_list"
                            ),
                        },
                    )
                    continue
            kr_items: List[Dict[str, str]] = []
            for kr in objective.get("kr_list", []):
                percent = kr.get("progress_rate", {}).get("percent")
                progress = ""
                if percent is not None:
                    if isinstance(percent, (int, float)):
                        progress = f"{percent:.0f}%"
                    else:
                        progress = str(percent)
                kr_items.append(
                    {
                        "id": kr.get("id", ""),
                        "title": (kr.get("content") or "").strip(),
                        "progress": progress,
                    }
                )
            objective_payload = {
                "id": objective.get("id", ""),
                "title": (objective.get("content") or "").strip(),
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "krs": kr_items,
            }
            for target in target_owner_ids:
                users[target].append(objective_payload)
    return {
        "users": [
            {"user_id": user_id, "objectives": objectives}
            for user_id, objectives in users.items()
        ]
    }


async def fetch_okrs_detail(
    token: str,
    okr_ids: List[str],
    timeout: float,
    trust_env: bool,
) -> List[Dict[str, Any]]:
    headers = {"Authorization": f"Bearer {token}"}
    okr_records: List[Dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=timeout, trust_env=trust_env) as client:
        for batch in chunked(okr_ids, 10):
            params = {
                "okr_ids": batch,
                "user_id_type": "open_id",
                "lang": "zh_cn",
            }
            response = await client.get(OKR_BATCH_GET_URL, params=params, headers=headers)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = ""
                try:
                    detail = json.dumps(response.json(), ensure_ascii=False)
                except Exception:
                    detail = response.text
                logger.error(
                    "okr_fetch_error",
                    extra={
                        "status": response.status_code,
                        "detail": detail,
                        "okr_ids": batch,
                    },
                )
                raise exc
            payload = response.json()
            if payload.get("code") != 0:
                raise RuntimeError(f"Failed to fetch OKR data: {payload}")
            okr_records.extend(payload.get("data", {}).get("okr_list", []))
    return okr_records


async def sync_okrs() -> None:
    settings = get_settings()
    if not settings.feishu_tenant_app_id or not settings.feishu_tenant_app_secret:
        raise RuntimeError("Tenant app credentials are required for OKR sync.")
    okr_ids_raw = settings.feishu_okr_ids or ""
    okr_ids = [okr_id.strip() for okr_id in okr_ids_raw.split(",") if okr_id.strip()]
    if not okr_ids:
        raise RuntimeError("FEISHU_OKR_IDS must be configured to sync OKR data.")

    token = await fetch_tenant_access_token(
        settings.feishu_tenant_app_id, settings.feishu_tenant_app_secret
    )
    logger.info(
        "okr_sync_start",
        extra={"token_obtained": bool(token), "okr_id_count": len(okr_ids)},
    )

    okr_records = await fetch_okrs_detail(
        token,
        okr_ids,
        timeout=settings.request_timeout,
        trust_env=settings.http_trust_env,
    )
    overrides = _parse_overrides(settings.feishu_okr_owner_overrides)
    cache_payload = _normalise_okrs(okr_records, overrides)

    cache_path = Path(settings.okr_cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(cache_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "okr_sync_written",
        extra={
            "cache_path": str(cache_path),
            "users": len(cache_payload.get("users", [])),
            "okr_records": len(okr_records),
        },
    )


def main() -> None:
    asyncio.run(sync_okrs())


if __name__ == "__main__":
    main()
