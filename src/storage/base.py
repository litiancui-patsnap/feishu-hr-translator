from __future__ import annotations

import abc
from typing import Protocol

from ..schemas import StoredReport


class StorageDriverProtocol(Protocol):
    async def save(self, record: StoredReport) -> None:
        ...


class StorageDriver(abc.ABC):
    @abc.abstractmethod
    async def save(self, record: StoredReport) -> None:
        """Persist the structured report."""
        raise NotImplementedError

