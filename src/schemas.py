from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

PeriodType = Literal["daily", "weekly", "monthly"]
RiskLevel = Literal["low", "medium", "high"]


class FeishuEventHeader(BaseModel):
    event_id: Optional[str] = None
    token: str
    event_type: Optional[str] = Field(default=None, alias="event_type")


class FeishuSender(BaseModel):
    user_id: Optional[str] = None
    open_id: Optional[str] = None
    union_id: Optional[str] = None
    name: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _normalise(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        sender_id = value.get("sender_id")
        if isinstance(sender_id, dict):
            combined = {**value, **sender_id}
            combined.pop("sender_id", None)
            return combined
        return value

    @property
    def preferred_user_id(self) -> str:
        return self.user_id or self.open_id or self.union_id or "unknown"


class FeishuMessage(BaseModel):
    message_id: str
    message_type: str
    content: str
    create_time: str
    sender: FeishuSender


class FeishuEventBody(BaseModel):
    message: FeishuMessage


class FeishuWebhookEnvelope(BaseModel):
    schema: Optional[str] = None
    header: FeishuEventHeader
    event: FeishuEventBody


class ReportIn(BaseModel):
    user_id: str
    user_name: str
    period_type: PeriodType
    period_start: date
    period_end: date
    raw_text: str
    message_ts: datetime


class RiskItem(BaseModel):
    item: str
    likelihood: RiskLevel
    mitigation: str


class NeedItem(BaseModel):
    topic: str
    owner: Optional[str] = None


class OKRAlignment(BaseModel):
    hit_objectives: List[str]
    hit_krs: List[str]
    gaps: List[str]
    confidence: float

    @field_validator("confidence")
    @classmethod
    def _validate_confidence(cls, value: float) -> float:
        return max(0.0, min(1.0, value))


class HRExtract(BaseModel):
    hr_summary: str
    risks: List[RiskItem]
    needs: List[NeedItem]
    okr_alignment: OKRAlignment
    next_actions: List[str]
    risk_level: RiskLevel


class StoredReport(BaseModel):
    report: ReportIn
    hr_extract: HRExtract
    okr_brief: str

    def to_csv_row(self) -> Dict[str, Any]:
        return {
            "user_id": self.report.user_id,
            "user_name": self.report.user_name,
            "period_type": self.report.period_type,
            "period_start": self.report.period_start.isoformat(),
            "period_end": self.report.period_end.isoformat(),
            "message_ts": self.report.message_ts.isoformat(),
            "raw_text": self.report.raw_text,
            "hr_summary": self.hr_extract.hr_summary,
            "risk_level": self.hr_extract.risk_level,
            "risks": "; ".join(
                f"{item.item}({item.likelihood})" for item in self.hr_extract.risks
            ),
            "needs": "; ".join(
                f"{item.topic}:{item.owner or '-'}" for item in self.hr_extract.needs
            ),
            "hit_objectives": "; ".join(
                self.hr_extract.okr_alignment.hit_objectives
            ),
            "hit_krs": "; ".join(self.hr_extract.okr_alignment.hit_krs),
            "okr_gaps": "; ".join(self.hr_extract.okr_alignment.gaps),
            "okr_confidence": f"{self.hr_extract.okr_alignment.confidence:.2f}",
            "next_actions": "; ".join(self.hr_extract.next_actions),
            "okr_brief": self.okr_brief,
        }
