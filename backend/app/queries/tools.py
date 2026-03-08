from sqlalchemy import text
from sqlmodel import Session
from datetime import datetime


def get_tool_usage(session: Session, days: int = 60, max_ts: datetime = None):
    """Tool usage ranking."""
    result = session.exec(text("""
        SELECT tool_name, COUNT(*) as usage_count
        FROM tool_results tr
        JOIN events e ON tr.event_id = e.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY tool_name
        ORDER BY usage_count DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{"tool_name": r[0], "usage_count": r[1]} for r in result]


def get_tool_success_rates(session: Session, days: int = 60, max_ts: datetime = None):
    """Success rate per tool."""
    result = session.exec(text("""
        SELECT
            tool_name,
            COUNT(*) as total,
            SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
            ROUND(AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)::numeric, 4) as success_rate,
            ROUND(AVG(duration_ms)::numeric, 1) as avg_duration_ms
        FROM tool_results tr
        JOIN events e ON tr.event_id = e.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY tool_name
        ORDER BY total DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{
        "tool_name": r[0],
        "total": r[1],
        "successes": r[2],
        "success_rate": float(r[3]),
        "avg_duration_ms": float(r[4]),
    } for r in result]


def get_tool_accept_reject(session: Session, days: int = 60, max_ts: datetime = None):
    """Tool accept/reject rates."""
    result = session.exec(text("""
        SELECT
            tool_name,
            decision,
            COUNT(*) as count
        FROM tool_decisions td
        JOIN events e ON td.event_id = e.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY tool_name, decision
        ORDER BY tool_name, decision
    """), params={"days": days, "max_ts": max_ts})
    return [{"tool_name": r[0], "decision": r[1], "count": r[2]} for r in result]


def get_rejection_sources(session: Session, days: int = 60, max_ts: datetime = None):
    """Rejection source breakdown."""
    result = session.exec(text("""
        SELECT source, COUNT(*) as count
        FROM tool_decisions td
        JOIN events e ON td.event_id = e.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
          AND td.decision = 'reject'
        GROUP BY source
        ORDER BY count DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{"source": r[0], "count": r[1]} for r in result]


def get_tools_by_practice(session: Session, days: int = 60, max_ts: datetime = None):
    """Tool usage grouped by practice."""
    result = session.exec(text("""
        SELECT
            e.user_practice,
            tr.tool_name,
            COUNT(*) as usage_count
        FROM tool_results tr
        JOIN events e ON tr.event_id = e.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
          AND e.user_practice IS NOT NULL
        GROUP BY e.user_practice, tr.tool_name
        ORDER BY e.user_practice, usage_count DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{"practice": r[0], "tool_name": r[1], "usage_count": r[2]} for r in result]
