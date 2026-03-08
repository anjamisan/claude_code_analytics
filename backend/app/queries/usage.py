from sqlalchemy import text
from sqlmodel import Session


def get_peak_hours(session: Session, days: int = 30):
    """Events by hour of day."""
    result = session.exec(text("""
        SELECT
            EXTRACT(HOUR FROM event_timestamp)::int as hour,
            COUNT(*) as event_count
        FROM events
        WHERE event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
        GROUP BY hour ORDER BY hour
    """), params={"days": days})
    return [{"hour": r[0], "event_count": r[1]} for r in result]


def get_usage_heatmap(session: Session, days: int = 30):
    """Events by hour × day-of-week."""
    result = session.exec(text("""
        SELECT
            EXTRACT(DOW FROM event_timestamp)::int as day_of_week,
            EXTRACT(HOUR FROM event_timestamp)::int as hour,
            COUNT(*) as event_count
        FROM events
        WHERE event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
        GROUP BY day_of_week, hour
        ORDER BY day_of_week, hour
    """), params={"days": days})
    return [{"day_of_week": r[0], "hour": r[1], "event_count": r[2]} for r in result]


def get_model_popularity(session: Session, days: int = 30):
    """Model usage distribution."""
    result = session.exec(text("""
        SELECT a.model, COUNT(*) as usage_count, SUM(a.cost_usd) as total_cost
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        WHERE e.event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
        GROUP BY a.model
        ORDER BY usage_count DESC
    """), params={"days": days})
    return [{"model": r[0], "usage_count": r[1], "total_cost": float(r[2])} for r in result]


def get_terminal_distribution(session: Session, days: int = 30):
    """Terminal type distribution."""
    result = session.exec(text("""
        SELECT terminal_type, COUNT(*) as event_count
        FROM events
        WHERE event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
          AND terminal_type IS NOT NULL
        GROUP BY terminal_type
        ORDER BY event_count DESC
    """), params={"days": days})
    return [{"terminal_type": r[0], "event_count": r[1]} for r in result]


def get_events_per_session(session: Session, days: int = 30):
    """Distribution of events per session."""
    result = session.exec(text("""
        SELECT
            session_id,
            COUNT(*) as event_count,
            MIN(event_timestamp) as start_time,
            MAX(event_timestamp) as end_time,
            EXTRACT(EPOCH FROM MAX(event_timestamp) - MIN(event_timestamp)) as duration_seconds
        FROM events
        WHERE event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
          AND session_id IS NOT NULL
        GROUP BY session_id
        ORDER BY event_count DESC
        LIMIT 100
    """), params={"days": days})
    return [{
        "session_id": str(r[0]),
        "event_count": r[1],
        "start_time": str(r[2]),
        "end_time": str(r[3]),
        "duration_seconds": float(r[4]) if r[4] else 0,
    } for r in result]


def get_os_distribution(session: Session, days: int = 30):
    """OS and architecture distribution."""
    result = session.exec(text("""
        SELECT os_type, host_arch, COUNT(*) as event_count
        FROM events
        WHERE event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
          AND os_type IS NOT NULL
        GROUP BY os_type, host_arch
        ORDER BY event_count DESC
    """), params={"days": days})
    return [{"os_type": r[0], "host_arch": r[1], "event_count": r[2]} for r in result]
