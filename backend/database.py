"""
Database configuration and session management.
"""
from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.config import get_settings

settings = get_settings()

# SQLite for development, can switch to PostgreSQL for production
DATABASE_URL = "sqlite:///./data/hr_translator.db"

# For PostgreSQL (production):
# DATABASE_URL = "postgresql://user:password@localhost/hr_translator"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Usage in FastAPI:
        @app.get("/items")
        async def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    Call this on application startup.
    """
    Base.metadata.create_all(bind=engine)
