from sqlalchemy import text
from sqlmodel import Session
from datetime import datetime


def get_token_trends(session: Session, days: int = 60, max_ts: datetime = None):
    """Daily token consumption trends."""
    result = session.exec(text("""
        SELECT
            DATE(e.event_timestamp) as date,
            SUM(a.input_tokens) as total_input,
            SUM(a.output_tokens) as total_output,
            SUM(a.cache_read_tokens) as total_cache_read,
            SUM(a.cache_creation_tokens) as total_cache_create
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY date ORDER BY date
    """), params={"days": days, "max_ts": max_ts})
    return [{
        "date": str(r[0]),
        "total_input": r[1],
        "total_output": r[2],
        "total_cache_read": r[3],
        "total_cache_create": r[4],
    } for r in result]


def get_tokens_by_practice(session: Session, days: int = 60, max_ts: datetime = None):
    """Token usage grouped by practice."""
    result = session.exec(text("""
        SELECT
            e.user_practice,
            SUM(a.input_tokens) as total_input,
            SUM(a.output_tokens) as total_output,
            SUM(a.cost_usd) as total_cost,
            COUNT(*) as num_requests
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
          AND e.user_practice IS NOT NULL
        GROUP BY e.user_practice
        ORDER BY total_cost DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{
        "practice": r[0],
        "total_input": r[1],
        "total_output": r[2],
        "total_cost": float(r[3]),
        "num_requests": r[4],
    } for r in result]


def get_tokens_by_level(session: Session, days: int = 60, max_ts: datetime = None):
    """Token usage grouped by employee level."""
    result = session.exec(text("""
        SELECT
            emp.level,
            SUM(a.input_tokens) as total_input,
            SUM(a.output_tokens) as total_output,
            AVG(a.cost_usd) as avg_cost,
            COUNT(*) as num_requests
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        JOIN employees emp ON e.user_email = emp.email
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY emp.level
        ORDER BY emp.level
    """), params={"days": days, "max_ts": max_ts})
    return [{
        "level": r[0],
        "total_input": r[1],
        "total_output": r[2],
        "avg_cost": float(r[3]),
        "num_requests": r[4],
    } for r in result]


def get_cache_efficiency(session: Session, days: int = 60, max_ts: datetime = None):
    """Cache hit ratio over time."""
    result = session.exec(text("""
        SELECT
            DATE(e.event_timestamp) as date,
            SUM(a.cache_read_tokens) as cache_read,
            SUM(a.cache_creation_tokens) as cache_create,
            CASE
                WHEN SUM(a.cache_read_tokens) + SUM(a.cache_creation_tokens) > 0
                THEN ROUND(SUM(a.cache_read_tokens)::numeric /
                    (SUM(a.cache_read_tokens) + SUM(a.cache_creation_tokens))::numeric, 4)
                ELSE 0
            END as cache_hit_ratio
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY date ORDER BY date
    """), params={"days": days, "max_ts": max_ts})
    return [{
        "date": str(r[0]),
        "cache_read": r[1],
        "cache_create": r[2],
        "cache_hit_ratio": float(r[3]),
    } for r in result]


def get_avg_cost_by_model(session: Session, days: int = 60, max_ts: datetime = None):
    """Average cost per request by model."""
    result = session.exec(text("""
        SELECT
            a.model,
            AVG(a.cost_usd) as avg_cost,
            AVG(a.input_tokens) as avg_input,
            AVG(a.output_tokens) as avg_output,
            COUNT(*) as num_requests
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY a.model
        ORDER BY avg_cost DESC
    """), params={"days": days, "max_ts": max_ts})
    return [{
        "model": r[0],
        "avg_cost": float(r[1]),
        "avg_input": float(r[2]),
        "avg_output": float(r[3]),
        "num_requests": r[4],
    } for r in result]


def get_input_output_ratio(session: Session, days: int = 60, max_ts: datetime = None):
    """Token input vs output ratio over time."""
    result = session.exec(text("""
        SELECT
            DATE(e.event_timestamp) as date,
            SUM(a.input_tokens) as total_input,
            SUM(a.output_tokens) as total_output,
            ROUND(AVG(a.input_tokens)::numeric, 1) as avg_input,
            ROUND(AVG(a.output_tokens)::numeric, 1) as avg_output,
            CASE
                WHEN SUM(a.output_tokens) > 0
                THEN ROUND(SUM(a.input_tokens)::numeric / SUM(a.output_tokens)::numeric, 2)
                ELSE 0
            END as input_output_ratio,
            COUNT(*) as num_requests
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        WHERE e.event_timestamp >= :max_ts - MAKE_INTERVAL(days => :days)
        GROUP BY date ORDER BY date
    """), params={"days": days, "max_ts": max_ts})
    return [{
        "date": str(r[0]),
        "total_input": r[1],
        "total_output": r[2],
        "avg_input": float(r[3]),
        "avg_output": float(r[4]),
        "input_output_ratio": float(r[5]),
        "num_requests": r[6],
    } for r in result]

