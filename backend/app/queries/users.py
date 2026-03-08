from sqlalchemy import text
from sqlmodel import Session


def get_user_ranking(session: Session, days: int = 30, limit: int = 20):
    """Most active users."""
    result = session.exec(text("""
        SELECT
            e.user_email,
            emp.full_name,
            emp.practice,
            emp.level,
            COUNT(*) as total_events,
            COUNT(DISTINCT e.session_id) as total_sessions
        FROM events e
        LEFT JOIN employees emp ON e.user_email = emp.email
        WHERE e.event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
        GROUP BY e.user_email, emp.full_name, emp.practice, emp.level
        ORDER BY total_events DESC
        LIMIT :limit
    """), params={"days": days, "limit": limit})
    return [{
        "user_email": r[0],
        "full_name": r[1],
        "practice": r[2],
        "level": r[3],
        "total_events": r[4],
        "total_sessions": r[5],
    } for r in result]


def get_prompt_stats(session: Session, days: int = 30):
    """Prompt length statistics."""
    result = session.exec(text("""
        SELECT
            ROUND(AVG(up.prompt_length)::numeric, 1) as avg_length,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY up.prompt_length) as median_length,
            MIN(up.prompt_length) as min_length,
            MAX(up.prompt_length) as max_length,
            COUNT(*) as total_prompts
        FROM events e
        JOIN user_prompts up ON e.event_id = up.event_id
        WHERE e.event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
    """), params={"days": days})
    row = result.one()
    return {
        "avg_length": float(row[0]) if row[0] else 0,
        "median_length": float(row[1]) if row[1] else 0,
        "min_length": row[2],
        "max_length": row[3],
        "total_prompts": row[4],
    }


def get_prompts_by_practice(session: Session, days: int = 30):
    """Prompt length by practice."""
    result = session.exec(text("""
        SELECT
            e.user_practice,
            ROUND(AVG(up.prompt_length)::numeric, 1) as avg_length,
            COUNT(*) as total_prompts
        FROM events e
        JOIN user_prompts up ON e.event_id = up.event_id
        WHERE e.event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
          AND e.user_practice IS NOT NULL
        GROUP BY e.user_practice
        ORDER BY avg_length DESC
    """), params={"days": days})
    return [{"practice": r[0], "avg_length": float(r[1]), "total_prompts": r[2]} for r in result]


def get_prompts_by_level(session: Session, days: int = 30):
    """Prompt length by employee level."""
    result = session.exec(text("""
        SELECT
            emp.level,
            ROUND(AVG(up.prompt_length)::numeric, 1) as avg_length,
            COUNT(*) as total_prompts
        FROM events e
        JOIN user_prompts up ON e.event_id = up.event_id
        JOIN employees emp ON e.user_email = emp.email
        WHERE e.event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
        GROUP BY emp.level
        ORDER BY emp.level
    """), params={"days": days})
    return [{"level": r[0], "avg_length": float(r[1]), "total_prompts": r[2]} for r in result]


def get_user_cost_breakdown(session: Session, days: int = 30, limit: int = 50):
    """Per-user cost breakdown."""
    result = session.exec(text("""
        SELECT
            e.user_email,
            emp.full_name,
            emp.practice,
            emp.level,
            SUM(a.cost_usd) as total_cost,
            SUM(a.input_tokens) as total_input,
            SUM(a.output_tokens) as total_output,
            COUNT(*) as num_requests
        FROM events e
        JOIN api_requests a ON e.event_id = a.event_id
        LEFT JOIN employees emp ON e.user_email = emp.email
        WHERE e.event_timestamp >= NOW() - MAKE_INTERVAL(days => :days)
        GROUP BY e.user_email, emp.full_name, emp.practice, emp.level
        ORDER BY total_cost DESC
        LIMIT :limit
    """), params={"days": days, "limit": limit})
    return [{
        "user_email": r[0],
        "full_name": r[1],
        "practice": r[2],
        "level": r[3],
        "total_cost": float(r[4]),
        "total_input": r[5],
        "total_output": r[6],
        "num_requests": r[7],
    } for r in result]
