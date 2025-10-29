from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..schemas import HRExtract, ReportIn


def build_summary_card(report: ReportIn, extract: HRExtract) -> Dict[str, Any]:
    report_date = report.message_ts.date().isoformat()
    kr_count = len(extract.okr_alignment.hit_krs)
    high_risks = [risk.item for risk in extract.risks if risk.likelihood == "high"]
    gaps = extract.okr_alignment.gaps
    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "plain_text",
                "content": f"{report.user_name}（{report.period_type}）\n{extract.hr_summary}",
            },
        }
    ]
    if high_risks:
        elements.append(
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"⚠️ 高风险: {', '.join(high_risks)}",
                    }
                ],
            }
        )
    if gaps:
        elements.append(
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": "仍需推进的目标：" + ", ".join(gaps),
                },
            }
        )
    if extract.next_actions:
        elements.append(
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": "下一步: " + "; ".join(extract.next_actions),
                },
            }
        )
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"{report_date} · OKR 对齐：{kr_count} KR",
            }
        },
        "elements": elements,
    }
