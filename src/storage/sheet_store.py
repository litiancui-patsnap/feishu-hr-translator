from __future__ import annotations

from typing import Optional

from ..schemas import StoredReport
from ..utils.logger import get_logger
from .base import StorageDriver

logger = get_logger(__name__)


class GoogleSheetStorage(StorageDriver):
    def __init__(self, service_account_json: str, sheet_id: str) -> None:
        self.service_account_json = service_account_json
        self.sheet_id = sheet_id
        logger.warning(
            "sheet_storage_placeholder",
            extra={
                "service_account_json": service_account_json,
                "sheet_id": sheet_id,
                "message": "Google Sheet integration not fully implemented in MVP.",
            },
        )

    async def save(self, record: StoredReport) -> None:
        raise NotImplementedError("Google Sheet storage not implemented in MVP.")

