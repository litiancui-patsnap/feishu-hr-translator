"""
API request/response schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============== Auth Schemas ==============


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    remember_me: bool = False


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class RegisterRequest(BaseModel):
    """User registration request."""

    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    username: str
    email: Optional[str]
    full_name: Optional[str]
    feishu_user_id: Optional[str]
    avatar_url: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime]
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============== Dashboard Schemas ==============


class DashboardStats(BaseModel):
    """Dashboard statistics."""

    weekly_reports: int
    monthly_reports: int
    high_risk_items: int
    okr_completion: float  # 0-100
    weekly_trend: float  # percentage change
    monthly_trend: float
    risk_trend: float
    okr_trend: float


class ReportSummary(BaseModel):
    """Report summary for dashboard."""

    id: int
    user_name: str
    period_type: str
    created_at: str
    risk_level: str
    hr_summary: str


class ReportDetail(BaseModel):
    """Full report details."""

    id: int
    user_id: str
    user_name: str
    period_type: str
    period_start: str
    period_end: str
    created_at: str  # message_ts
    raw_text: str
    hr_summary: str
    risk_level: str
    risks: Optional[str]
    needs: Optional[str]
    hit_objectives: Optional[str]
    hit_krs: Optional[str]
    okr_gaps: Optional[str]
    okr_confidence: Optional[str]
    next_actions: Optional[str]
    okr_brief: Optional[str]


class RiskDistribution(BaseModel):
    """Risk distribution data."""

    low: int
    medium: int
    high: int
