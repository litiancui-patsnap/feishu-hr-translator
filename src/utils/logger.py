from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict

_INITIALISED = False


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in payload:
                continue
            if key in {"msg", "args", "levelname", "levelno", "pathname", "filename"}:
                continue
            if key in {"module", "funcName", "lineno", "created"}:
                continue
            payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    global _INITIALISED
    if _INITIALISED:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]
    _INITIALISED = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)

