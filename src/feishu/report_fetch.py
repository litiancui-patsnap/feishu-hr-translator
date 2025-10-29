from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, time
from pathlib import Path
from typing import Iterable, List, Optional, Dict

import httpx

from ..ai.qwen import QwenClient
from ..config import get_settings
from ..feishu.api_client import FeishuAPIClient
from ..feishu.cards import build_summary_card
from ..okr.source import OKRSource, build_okr_source
from ..okr.sync_job import fetch_tenant_access_token
from ..schemas import ReportIn, StoredReport
from ..storage import build_storage
from ..storage.base import StorageDriver
from ..utils.logger import get_logger
from ..utils.period import detect_period

logger = get_logger(__name__)

REPORT_QUERY_URL = "https://open.feishu.cn/open-apis/report/v1/tasks/query"


@dataclass
class ReportTask:
    task_id: str
    rule_id: str
    rule_name: str
    user_id: str
    user_name: str
    commit_time: datetime
    text: str


def _load_processed(cache_path: Path) -> set[str]:
    if not cache_path.exists():
        return set()
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        items = data.get("processed", [])
        return set(str(item) for item in items)
    except Exception as exc:
        logger.error("report_cache_load_failed", extra={"error": str(exc)})
        return set()


def _save_processed(cache_path: Path, processed: Iterable[str]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"processed": list(processed)}
    cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _period_from_rule(rule_period: str, commit_dt: datetime) -> tuple[str, date, date]:
    rule_period = rule_period.lower()
    commit_date = commit_dt.date()
    if rule_period == "daily":
        return "daily", commit_date, commit_date
    if rule_period == "weekly":
        start = commit_date - timedelta(days=commit_date.weekday())
        end = start + timedelta(days=6)
        return "weekly", start, end
    if rule_period == "monthly":
        start = commit_date.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        return "monthly", start, end
    # fallback: detect by text
    period_type, start, end = detect_period("", commit_date)
    return period_type, start, end


def _build_text(rule_name: str, form_contents: List[Dict[str, str]]) -> str:
    lines = [f"【规则】{rule_name}"]
    for content in form_contents or []:
        name = (content.get("field_name") or "").strip()
        value = (content.get("field_value") or "").strip()
        if not value:
            continue
        if name:
            lines.append(f"{name}: {value}")
        else:
            lines.append(value)
    return "\n".join(lines)


async def _fetch_reports_for_rule(
    client: httpx.AsyncClient,
    token: str,
    rule_id: str,
    start_ts: int,
    end_ts: int,
    period_type: str,
) -> List[ReportTask]:
    headers = {"Authorization": f"Bearer {token}"}
    page_token = ""
    results: List[ReportTask] = []
    while True:
        body = {
            "page_token": page_token,
            "commit_start_time": start_ts,
            "commit_end_time": end_ts,
            "page_size": 20,
            "rule_id": rule_id,
        }
        response = await client.post(REPORT_QUERY_URL, headers=headers, json=body)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            logger.error(
                "report_query_error",
                extra={
                    "status_code": response.status_code,
                    "detail": detail,
                    "rule_id": rule_id,
                    "request_body": body,
                },
            )
            raise exc
        payload = response.json()
        if payload.get("code") != 0:
            raise RuntimeError(f"query report failed: {payload}")
        data = payload.get("data") or {}
        items = data.get("items") or []
        for item in items:
            commit_time = datetime.utcfromtimestamp(item.get("commit_time", end_ts))
            text = _build_text(item.get("rule_name", ""), item.get("form_contents") or [])
            results.append(
                ReportTask(
                    task_id=str(item.get("task_id")),
                    rule_id=str(item.get("rule_id")),
                    rule_name=item.get("rule_name", ""),
                    user_id=item.get("from_user_id", ""),
                    user_name=item.get("from_user_name", ""),
                    commit_time=commit_time,
                    text=text,
                )
            )
        if not data.get("has_more"):
            break
        page_token = data.get("page_token") or ""
        if not page_token:
            break
    return results


async def fetch_reports(start_ts: Optional[int] = None, end_ts: Optional[int] = None) -> None:
    settings = get_settings()
    rules = settings.parse_report_rules()
    if not rules:
        logger.warning("report_rules_not_configured")
        return
    if not settings.feishu_tenant_app_id or not settings.feishu_tenant_app_secret:
        raise RuntimeError("Tenant app credentials are required to fetch reports.")

    token = await fetch_tenant_access_token(
        settings.feishu_tenant_app_id, settings.feishu_tenant_app_secret
    )

    now_ts = int(datetime.utcnow().timestamp())
    if end_ts is None:
        end_ts = now_ts
    if start_ts is None:
        start_ts = end_ts - settings.feishu_report_lookback_hours * 3600

    logger.info(
        "report_fetch_start",
        extra={
            "rules": len(rules),
            "start_ts": start_ts,
            "end_ts": end_ts,
        },
    )
    cache_path = Path(settings.feishu_report_cache_path)
    processed = _load_processed(cache_path)

    storage: StorageDriver = build_storage(settings)
    okr_source: OKRSource = build_okr_source(settings)
    feishu_client = FeishuAPIClient(
        app_id=settings.feishu_app_id,
        app_secret=settings.feishu_app_secret,
        default_chat_id=settings.feishu_default_chat_id,
        timeout=settings.request_timeout,
        trust_env=settings.http_trust_env,
    )
    qwen_client = QwenClient(
        api_key=settings.dashscope_api_key,
        model=settings.qwen_model,
        timeout=settings.request_timeout,
        api_mode=settings.qwen_api_mode,
        trust_env=settings.http_trust_env,
    )

    async with httpx.AsyncClient(timeout=settings.request_timeout, trust_env=settings.http_trust_env) as client:
        for rule_id, period in rules:
            tasks = await _fetch_reports_for_rule(
                client, token, rule_id, start_ts, end_ts, period
            )
            for task in tasks:
                if task.task_id in processed:
                    continue
                period_type, period_start, period_end = _period_from_rule(
                    period, task.commit_time
                )
                report = ReportIn(
                    user_id=task.user_id or "unknown",
                    user_name=task.user_name or task.user_id or "unknown",
                    period_type=period_type,
                    period_start=period_start,
                    period_end=period_end,
                    raw_text=task.text,
                    message_ts=task.commit_time,
                )
                okr_brief = await okr_source.get_okr_brief(
                    report.user_id, period_start, period_end
                )
                extract = await qwen_client.generate_hr_extract(report, okr_brief)
                record = StoredReport(report=report, hr_extract=extract, okr_brief=okr_brief)
                await storage.save(record)
                card = build_summary_card(report, extract)
                await feishu_client.send_card(card)
                processed.add(task.task_id)
                logger.info(
                    "report_task_processed",
                    extra={
                        "task_id": task.task_id,
                        "user_id": report.user_id,
                        "period_type": report.period_type,
                    },
                )

    _save_processed(cache_path, processed)
    logger.info("report_fetch_completed", extra={"processed": len(processed)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Feishu report tasks.")
    parser.add_argument(
        "--start",
        help="起始日期 YYYY-MM-DD，默认根据 LOOKBACK_HOURS 计算",
    )
    parser.add_argument(
        "--end",
        help="结束日期 YYYY-MM-DD，默认当前时间",
    )
    args = parser.parse_args()

    start_ts = None
    end_ts = None
    if args.start:
        start_date = datetime.fromisoformat(args.start).date()
        start_dt = datetime.combine(start_date, time.min)
        start_ts = int(start_dt.timestamp())
    if args.end:
        end_date = datetime.fromisoformat(args.end).date()
        end_dt = datetime.combine(end_date, time.max)
        end_ts = int(end_dt.timestamp())

    asyncio.run(fetch_reports(start_ts=start_ts, end_ts=end_ts))


if __name__ == "__main__":
    main()
