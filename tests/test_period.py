from datetime import date

import pytest

from src.utils.period import detect_period


@pytest.mark.parametrize(
    "text,reference,expected_type",
    [
        ("这是今天的日报", date(2024, 5, 10), "daily"),
        ("本周周报总结", date(2024, 5, 10), "weekly"),
        ("月报：四月交付情况", date(2024, 4, 15), "monthly"),
        ("Summary of this week", date(2024, 1, 31), "weekly"),
        ("Summary for today", date(2024, 6, 1), "daily"),
    ],
)
def test_detect_period_types(text, reference, expected_type):
    period_type, start, end = detect_period(text, reference)
    assert period_type == expected_type
    assert start <= end


def test_detect_period_weekly_window():
    text = "周报：完成支付系统优化"
    reference = date(2024, 3, 6)  # Wednesday
    period_type, start, end = detect_period(text, reference)
    assert period_type == "weekly"
    assert start.weekday() == 0
    assert end.weekday() == 6


def test_detect_period_monthly_window():
    text = "Monthly review"
    reference = date(2024, 2, 15)
    period_type, start, end = detect_period(text, reference)
    assert period_type == "monthly"
    assert start == date(2024, 2, 1)
    assert end == date(2024, 2, 29)
