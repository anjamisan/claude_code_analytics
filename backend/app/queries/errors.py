from sqlalchemy import text
from sqlmodel import Session
from datetime import datetime


def get_error_rate(session: Session, days: int = 60, max_ts: datetime = None):
    """Error rate over time."""
    result = session.exec(text("""
        SELECT
            DATE(e.event_timestamp) as date,
            COUNT(*) as error_count
        FROM events e
        JOIN api_errors ae ON e.event_id = ae.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY date ORDER BY date
    """), params={"days": days, "max_ts": max_ts})
    return [{"date": str(r[0]), "error_count": r[1]} for r in result]


def get_errors_by_status(session: Session, days: int = 60, max_ts: datetime = None):
    """Errors grouped by status code."""
    result = session.exec(text("""
        SELECT ae.status_code, COUNT(*) as count
        FROM events e
        JOIN api_errors ae ON e.event_id = ae.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY ae.status_code
        ORDER BY count DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{"status_code": r[0], "count": r[1]} for r in result]


def get_errors_by_model(session: Session, days: int = 60, max_ts: datetime = None):
    """Errors grouped by model."""
    result = session.exec(text("""
        SELECT ae.model, COUNT(*) as count
        FROM events e
        JOIN api_errors ae ON e.event_id = ae.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
          AND ae.model IS NOT NULL
        GROUP BY ae.model
        ORDER BY count DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{"model": r[0], "count": r[1]} for r in result]


def get_retry_distribution(session: Session, days: int = 60, max_ts: datetime = None):
    """Distribution of retry attempts."""
    result = session.exec(text("""
        SELECT ae.attempt, COUNT(*) as count
        FROM events e
        JOIN api_errors ae ON e.event_id = ae.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY ae.attempt
        ORDER BY ae.attempt
    """), params={"days": days, "max_ts": max_ts})
    return [{"attempt": r[0], "count": r[1]} for r in result]


def get_top_error_messages(session: Session, days: int = 60, limit: int = 10, max_ts: datetime = None):
    """Most common error messages."""
    result = session.exec(text("""
        SELECT ae.error_message, COUNT(*) as count
        FROM events e
        JOIN api_errors ae ON e.event_id = ae.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
          AND ae.error_message IS NOT NULL AND ae.error_message != ''
        GROUP BY ae.error_message
        ORDER BY count DESC
        LIMIT :limit
    """), params={"days": days, "limit": limit, "max_ts": max_ts})
    return [{"error_message": r[0], "count": r[1]} for r in result]
