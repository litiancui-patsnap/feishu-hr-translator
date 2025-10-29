from __future__ import annotations

from datetime import time as dt_time
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

StorageDriver = Literal["csv", "sheet", "bitable"]
OKRSourceType = Literal["cache", "sheet", "bitable"]


class Settings(BaseSettings):
    """Application runtime configuration parsed from environment variables."""

    app_port: int = Field(default=8080, alias="APP_PORT")
    base_url: str = Field(default="http://localhost:8080", alias="APP_BASE_URL")

    feishu_app_id: Optional[str] = Field(default=None, alias="FEISHU_APP_ID")
    feishu_app_secret: Optional[str] = Field(default=None, alias="FEISHU_APP_SECRET")
    feishu_bot_verification_token: str = Field(
        default="", alias="FEISHU_BOT_VERIFICATION_TOKEN"
    )
    feishu_bot_encrypt_key: Optional[str] = Field(
        default=None, alias="FEISHU_BOT_ENCRYPT_KEY"
    )
    feishu_default_chat_id: Optional[str] = Field(
        default=None, alias="FEISHU_DEFAULT_CHAT_ID"
    )

    dashscope_api_key: Optional[str] = Field(default=None, alias="DASHSCOPE_API_KEY")
    qwen_model: str = Field(default="qwen-max", alias="QWEN_MODEL")
    qwen_api_mode: Literal["text", "compatible"] = Field(
        default="text", alias="QWEN_API_MODE"
    )

    storage_driver: StorageDriver = Field(default="csv", alias="STORAGE_DRIVER")
    csv_path: str = Field(default="./data/reports_slim.csv", alias="CSV_PATH")

    google_service_account_json: Optional[str] = Field(
        default=None, alias="GOOGLE_SERVICE_ACCOUNT_JSON"
    )
    google_sheet_id: Optional[str] = Field(default=None, alias="GOOGLE_SHEET_ID")

    feishu_tenant_key: Optional[str] = Field(default=None, alias="FEISHU_TENANT_KEY")
    bitable_base_id: Optional[str] = Field(default=None, alias="BITABLE_BASE_ID")
    bitable_table_id: Optional[str] = Field(default=None, alias="BITABLE_TABLE_ID")

    okr_source: OKRSourceType = Field(default="cache", alias="OKR_SOURCE")
    okr_cache_path: str = Field(default="./data/okr_cache.json", alias="OKR_CACHE_PATH")

    feishu_tenant_app_id: Optional[str] = Field(
        default=None, alias="FEISHU_TENANT_APP_ID"
    )
    feishu_tenant_app_secret: Optional[str] = Field(
        default=None, alias="FEISHU_TENANT_APP_SECRET"
    )
    feishu_okr_ids: Optional[str] = Field(default=None, alias="FEISHU_OKR_IDS")
    feishu_okr_owner_overrides: Optional[str] = Field(
        default=None, alias="FEISHU_OKR_OWNER_OVERRIDES"
    )
    feishu_report_rules: Optional[str] = Field(
        default=None, alias="FEISHU_REPORT_RULES"
    )
    feishu_report_lookback_hours: int = Field(
        default=72, alias="FEISHU_REPORT_LOOKBACK_HOURS"
    )
    feishu_report_cache_path: str = Field(
        default="./data/report_task_cache.json", alias="FEISHU_REPORT_CACHE_PATH"
    )

    auto_sync_enabled: bool = Field(default=False, alias="AUTO_SYNC_ENABLED")
    auto_sync_time: str = Field(default="02:00", alias="AUTO_SYNC_TIME")
    auto_sync_lookback_hours: int = Field(
        default=24, alias="AUTO_SYNC_LOOKBACK_HOURS"
    )
    auto_sync_run_on_start: bool = Field(
        default=False, alias="AUTO_SYNC_RUN_ON_START"
    )

    request_timeout: float = Field(default=10.0, alias="REQUEST_TIMEOUT_SECONDS")
    http_trust_env: bool = Field(default=False, alias="HTTP_TRUST_ENV")

    model_config = SettingsConfigDict(populate_by_name=True, extra="ignore")

    @field_validator("storage_driver")
    @classmethod
    def _validate_storage_driver(cls, value: StorageDriver) -> StorageDriver:
        return value.lower()  # type: ignore[return-value]

    @field_validator("okr_source")
    @classmethod
    def _validate_okr_source(cls, value: OKRSourceType) -> OKRSourceType:
        return value.lower()  # type: ignore[return-value]

    @field_validator("csv_path", "okr_cache_path", mode="before")
    @classmethod
    def _expand_path(cls, value: str) -> str:
        return str(Path(value).expanduser())

    @field_validator("auto_sync_time")
    @classmethod
    def _validate_auto_sync_time(cls, value: str) -> str:
        parts = value.split(":")
        if len(parts) != 2:
            raise ValueError("AUTO_SYNC_TIME must be in HH:MM 24-hour format.")
        hour, minute = parts
        if not (hour.isdigit() and minute.isdigit()):
            raise ValueError("AUTO_SYNC_TIME must be numeric HH:MM.")
        hour_int = int(hour)
        minute_int = int(minute)
        if not (0 <= hour_int <= 23 and 0 <= minute_int <= 59):
            raise ValueError("AUTO_SYNC_TIME must be a valid time of day.")
        return f"{hour_int:02d}:{minute_int:02d}"

    @model_validator(mode="after")
    def _adjust_qwen_mode(self) -> "Settings":
        if (
            self.qwen_api_mode == "text"
            and self.qwen_model.lower() in {"qwen-plus", "qwen-long", "qwen-turbo"}
        ):
            object.__setattr__(self, "qwen_api_mode", "compatible")
        return self

    def parse_report_rules(self) -> list[tuple[str, str]]:
        """Parse FEISHU_REPORT_RULES into a list of (rule_id, period_type)."""
        if not self.feishu_report_rules:
            return []
        rules: list[tuple[str, str]] = []
        for raw in self.feishu_report_rules.split(";"):
            raw = raw.strip()
            if not raw or ":" not in raw:
                continue
            rule_id, period_type = raw.split(":", 1)
            rules.append((rule_id.strip(), period_type.strip().lower()))
        return rules

    def get_auto_sync_time(self) -> dt_time:
        hour_str, minute_str = self.auto_sync_time.split(":")
        return dt_time(hour=int(hour_str), minute=int(minute_str))


def load_settings() -> Settings:
    """Load .env first, then parse environment variables."""
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)  # idempotent
    return Settings()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()
