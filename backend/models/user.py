"""
User and authentication models.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)  # NULL for OAuth users
    full_name = Column(String(200), nullable=True)

    # Feishu integration
    feishu_user_id = Column(String(100), unique=True, nullable=True, index=True)
    feishu_open_id = Column(String(100), nullable=True)
    feishu_union_id = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Role and status
    role = Column(String(20), default="user", nullable=False)  # admin, hr, user
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    def to_dict(self) -> dict:
        """Convert user to dictionary (for API responses)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "feishu_user_id": self.feishu_user_id,
            "avatar_url": self.avatar_url,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }


class UserSession(Base):
    """User session model for tracking JWT tokens."""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    access_token = Column(String(500), nullable=False, index=True)
    refresh_token = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=False)

    # Session metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"
