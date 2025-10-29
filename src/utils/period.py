from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Tuple

from ..schemas import PeriodType

DAILY_KEYWORDS = {"日报", "日報", "daily", "today", "当日", "本日"}
WEEKLY_KEYWORDS = {"周报", "週報", "weekly", "this week", "本周", "本週"}
MONTHLY_KEYWORDS = {"月报", "月度", "monthly", "this month", "本月"}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _contains_keyword(text: str, keywords: set[str]) -> bool:
    lower_text = text.lower()
    return any(keyword.lower() in lower_text for keyword in keywords)


def detect_period(
    text: str, reference: date | None = None
) -> Tuple[PeriodType, date, date]:
    """Infer the reporting period window from the message text."""
    reference_date = reference or date.today()
    normalized = _normalize(text)
    if _contains_keyword(normalized, MONTHLY_KEYWORDS):
        period_type: PeriodType = "monthly"
        start = reference_date.replace(day=1)
        # Next month first day minus one
        if reference_date.month == 12:
            next_month = reference_date.replace(year=reference_date.year + 1, month=1, day=1)
        else:
            next_month = reference_date.replace(month=reference_date.month + 1, day=1)
        end = next_month - timedelta(days=1)
        return period_type, start, end

    if _contains_keyword(normalized, WEEKLY_KEYWORDS):
        period_type = "weekly"
        start = reference_date - timedelta(days=reference_date.weekday())
        end = start + timedelta(days=6)
        return period_type, start, end

    if _contains_keyword(normalized, DAILY_KEYWORDS):
        period_type = "daily"
        return period_type, reference_date, reference_date

    # Fallback heuristic: treat as weekly report near end of week, otherwise daily.
    if reference_date.weekday() in {4, 5, 6}:  # Fri/Sat/Sun
        start = reference_date - timedelta(days=reference_date.weekday())
        end = start + timedelta(days=6)
        return "weekly", start, end

    return "daily", reference_date, reference_date

