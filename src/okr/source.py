from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Protocol

from ..config import Settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OKRSource(Protocol):
    async def get_okr_brief(
        self, user_id: str, period_start: date, period_end: date
    ) -> str:
        ...


@dataclass
class OKRRecord:
    objective_id: str
    objective_title: str
    period_start: date
    period_end: date
    krs: List[Dict[str, str]]


class CacheOKRSource:
    def __init__(self, cache_path: str) -> None:
        self.cache_path = Path(cache_path)
        self._data: Optional[Dict[str, List[OKRRecord]]] = None

    async def get_okr_brief(
        self, user_id: str, period_start: date, period_end: date
    ) -> str:
        data = await asyncio.to_thread(self._load_cache)
        user_records = data.get(user_id, [])
        overlapping = [
            record
            for record in user_records
            if _ranges_overlap(record.period_start, record.period_end, period_start, period_end)
        ]
        logger.info(
            "okr_cache_hit",
            extra={
                "user_id": user_id,
                "records_total": len(user_records),
                "records_overlap": len(overlapping),
            },
        )
        if not overlapping:
            return "未找到该周期的OKR信息。"
        parts: List[str] = []
        for record in overlapping:
            date_window = f"{record.period_start.isoformat()}~{record.period_end.isoformat()}"
            parts.append(f"{record.objective_id} {record.objective_title} ({date_window})")
            for kr in record.krs:
                progress = kr.get("progress", "")
                parts.append(f"- {kr.get('id','KR?')} {kr.get('title','')} {progress}")
        return "\n".join(parts)

    def _load_cache(self) -> Dict[str, List[OKRRecord]]:
        if self._data is not None:
            return self._data
        if not self.cache_path.exists():
            logger.warning(
                "okr_cache_missing", extra={"cache_path": str(self.cache_path)}
            )
            self._data = {}
            return self._data
        with self.cache_path.open("r", encoding="utf-8") as fp:
            raw = json.load(fp)
        users = raw.get("users", [])
        data: Dict[str, List[OKRRecord]] = {}
        for user in users:
            uid = user.get("user_id")
            if not uid:
                continue
            records: List[OKRRecord] = []
            for obj in user.get("objectives", []):
                records.append(
                    OKRRecord(
                        objective_id=obj.get("id", "O?"),
                        objective_title=obj.get("title", ""),
                        period_start=_parse_date(obj.get("period_start")),
                        period_end=_parse_date(obj.get("period_end")),
                        krs=obj.get("krs", []),
                    )
                )
            data[uid] = records
        self._data = data
        return self._data


class NullOKRSource:
    async def get_okr_brief(
        self, user_id: str, period_start: date, period_end: date
    ) -> str:
        logger.warning(
            "okr_source_unavailable",
            extra={
                "user_id": user_id,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
            },
        )
        return "OKR数据暂不可用。"


def _ranges_overlap(
    a_start: date, a_end: date, b_start: date, b_end: date
) -> bool:
    return a_start <= b_end and b_start <= a_end


def _parse_date(value: Optional[str]) -> date:
    if not value:
        return date.today()
    return datetime.fromisoformat(value).date()


def build_okr_source(settings: Settings) -> OKRSource:
    if settings.okr_source == "cache":
        return CacheOKRSource(settings.okr_cache_path)
    if settings.okr_source in {"sheet", "bitable"}:
        logger.warning(
            "okr_source_placeholder",
            extra={"okr_source": settings.okr_source, "message": "Only cache implemented."},
        )
        return NullOKRSource()
    raise ValueError(f"Unsupported OKR source: {settings.okr_source}")

