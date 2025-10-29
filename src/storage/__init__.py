from __future__ import annotations

from ..config import Settings
from ..utils.logger import get_logger
from .base import StorageDriver
from .bitable_store import BitableStorage
from .csv_store import CSVStorage
from .sheet_store import GoogleSheetStorage

logger = get_logger(__name__)


def build_storage(settings: Settings) -> StorageDriver:
    driver = settings.storage_driver
    if driver == "csv":
        logger.info("storage_selected", extra={"driver": driver, "path": settings.csv_path})
        return CSVStorage(settings.csv_path)
    if driver == "sheet":
        if not settings.google_service_account_json or not settings.google_sheet_id:
            raise ValueError("Google Sheet storage requires credentials and sheet id.")
        logger.info(
            "storage_selected",
            extra={
                "driver": driver,
                "sheet_id": settings.google_sheet_id,
            },
        )
        return GoogleSheetStorage(
            settings.google_service_account_json, settings.google_sheet_id
        )
    if driver == "bitable":
        if not settings.bitable_base_id or not settings.bitable_table_id:
            raise ValueError("Bitable storage requires base and table id.")
        logger.info(
            "storage_selected",
            extra={
                "driver": driver,
                "base_id": settings.bitable_base_id,
                "table_id": settings.bitable_table_id,
            },
        )
        return BitableStorage(
            settings.feishu_tenant_key,
            settings.bitable_base_id,
            settings.bitable_table_id,
        )
    raise ValueError(f"Unsupported storage driver: {driver}")

