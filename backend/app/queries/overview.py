from sqlalchemy import text
from sqlmodel import Session
from datetime import datetime


def get_total_cost(session: Session, days: int = 60, max_ts: datetime = None):
    """Total cost over time (daily)."""
    result = session.exec(text("""
        SELECT DATE(e.event_timestamp) as date, SUM(a.cost_usd) as total_cost
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY date ORDER BY date
    """), params={"days": days, "max_ts": max_ts})
    return [{"date": str(r[0]), "total_cost": float(r[1])} for r in result]


def get_active_users(session: Session, days: int = 60, max_ts: datetime = None):
    """Active users per day."""
    result = session.exec(text("""
        SELECT DATE(event_timestamp) as date, COUNT(DISTINCT user_email) as active_users
        FROM events
        WHERE event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY date ORDER BY date
    """), params={"days": days, "max_ts": max_ts})
    return [{"date": str(r[0]), "active_users": r[1]} for r in result]


def get_summary_stats(session: Session, days: int = 60, max_ts: datetime = None):
    """High-level summary: total events, sessions, users, cost."""
    result = session.exec(text("""
        SELECT
            COUNT(*) as total_events,
            COUNT(DISTINCT session_id) as total_sessions,
            COUNT(DISTINCT user_email) as total_users
        FROM events
        WHERE event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
    """), params={"days": days, "max_ts": max_ts})
    row = result.one()
    
    cost_result = session.exec(text("""
        SELECT COALESCE(SUM(a.cost_usd), 0) as total_cost
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
    """), params={"days": days, "max_ts": max_ts})
    total_cost = float(cost_result.one()[0])

    return {
        "total_events": row[0],
        "total_sessions": row[1],
        "total_users": row[2],
        "total_cost": total_cost,
    }


def get_cost_by_practice(session: Session, days: int = 60, max_ts: datetime = None):
    """Total cost grouped by practice."""
    result = session.exec(text("""
        SELECT e.user_practice, SUM(a.cost_usd) as total_cost, COUNT(*) as num_requests
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
          AND e.user_practice IS NOT NULL
        GROUP BY e.user_practice
        ORDER BY total_cost DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{"practice": r[0], "total_cost": float(r[1]), "num_requests": r[2]} for r in result]


def get_cost_by_level(session: Session, days: int = 60, max_ts: datetime = None):
    """Total cost grouped by employee level."""
    result = session.exec(text("""
        SELECT emp.level, SUM(a.cost_usd) as total_cost, COUNT(*) as num_requests
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        JOIN employees emp ON e.user_email = emp.email
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY emp.level
        ORDER BY emp.level
    """), params={"days": days, "max_ts": max_ts})
    return [{"level": r[0], "total_cost": float(r[1]), "num_requests": r[2]} for r in result]


def get_cost_by_location(session: Session, days: int = 60, max_ts: datetime = None):
    """Total cost grouped by employee location."""
    result = session.exec(text("""
        SELECT emp.location, SUM(a.cost_usd) as total_cost, COUNT(*) as num_requests
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        JOIN employees emp ON e.user_email = emp.email
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY emp.location
        ORDER BY total_cost DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{"location": r[0], "total_cost": float(r[1]), "num_requests": r[2]} for r in result]
