from __future__ import annotations

import asyncio
import csv
from pathlib import Path
from typing import List

from ..schemas import StoredReport
from ..utils.logger import get_logger
from .base import StorageDriver

logger = get_logger(__name__)


class CSVStorage(StorageDriver):
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.headers: List[str] = [
            "user_id",
            "user_name",
            "period_type",
            "period_start",
            "period_end",
            "message_ts",
            "raw_text",
            "hr_summary",
            "risk_level",
            "risks",
            "needs",
            "hit_objectives",
            "hit_krs",
            "okr_gaps",
            "okr_confidence",
            "next_actions",
            "okr_brief",
        ]
        self._ensure_header()

    def _ensure_header(self) -> None:
        if not self.path.exists() or self.path.stat().st_size == 0:
            with self.path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=self.headers)
                writer.writeheader()

    async def save(self, record: StoredReport) -> None:
        await asyncio.to_thread(self._write_row, record)

    def _write_row(self, record: StoredReport) -> None:
        row = record.to_csv_row()
        with self.path.open("a", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=self.headers)
            writer.writerow(row)
        logger.info(
            "report_saved",
            extra={
                "storage": "csv",
                "path": str(self.path),
                "user_id": record.report.user_id,
            },
        )

