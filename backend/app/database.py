from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy import text
from backend.app.config import settings
from datetime import datetime
from typing import Optional
import time

# Import all models so SQLModel.metadata knows about them
import backend.app.models.models as _models  # noqa: F401


# Create engine with proper configuration
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.FASTAPI_DEBUG,
    future=True,
    pool_pre_ping=True,  # Verify connections before using
)


# Cached max timestamp (avoids repeated subqueries)
_max_ts_cache: Optional[datetime] = None
_max_ts_cached_at: float = 0
_MAX_TS_TTL: int = 300  # refresh every 5 minutes


def get_max_event_timestamp(session: Session) -> datetime:
    """Get the latest event timestamp, cached in memory."""
    global _max_ts_cache, _max_ts_cached_at
    now = time.monotonic()
    if _max_ts_cache is None or (now - _max_ts_cached_at) > _MAX_TS_TTL:
        result = session.exec(text("SELECT MAX(event_timestamp) FROM events"))
        _max_ts_cache = result.one()[0]
        _max_ts_cached_at = now
    return _max_ts_cache


def create_db_and_tables():
    """Create all database tables on startup"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for FastAPI to get database session"""
    with Session(engine) as session:
        yield session


async def close_db_connection():
    """Close the database engine connection"""
    engine.dispose()