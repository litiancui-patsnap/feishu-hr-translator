from __future__ import annotations

from ..schemas import StoredReport
from ..utils.logger import get_logger
from .base import StorageDriver

logger = get_logger(__name__)


class BitableStorage(StorageDriver):
    def __init__(self, tenant_key: str | None, base_id: str, table_id: str) -> None:
        self.tenant_key = tenant_key
        self.base_id = base_id
        self.table_id = table_id
        logger.warning(
            "bitable_storage_placeholder",
            extra={
                "tenant_key": tenant_key,
                "base_id": base_id,
                "table_id": table_id,
                "message": "Bitable integration not fully implemented in MVP.",
            },
        )

    async def save(self, record: StoredReport) -> None:
        raise NotImplementedError("Bitable storage not implemented in MVP.")

