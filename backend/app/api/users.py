from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session, get_max_event_timestamp
from backend.app.queries import users as q

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/ranking") #User activity ranking — most active users
def user_ranking(days: int = Query(60, ge=1, le=365), limit: int = Query(20, ge=1, le=100), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_user_ranking(session, days, limit, max_ts=max_ts)


@router.get("/prompt-stats") # Prompt length by employee level — avg prompt length and prompt count per level
def prompt_stats(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_prompt_stats(session, days, max_ts=max_ts)


@router.get("/prompts-by-practice") #Prompt length by practice
def prompts_by_practice(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_prompts_by_practice(session, days, max_ts=max_ts)


@router.get("/prompts-by-level") #Prompt length by user level 
def prompts_by_level(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_prompts_by_level(session, days, max_ts=max_ts)


@router.get("/cost-breakdown") #Cost breakdown by user — who are the top spenders and what’s driving their costs (input vs output tokens, etc.)
def cost_breakdown(days: int = Query(60, ge=1, le=365), limit: int = Query(50, ge=1, le=200), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_user_cost_breakdown(session, days, limit, max_ts=max_ts)

@router.get("/least-active") #Least active users
def least_active_users(days: int = Query(60, ge=1, le=365), limit: int = Query(20, ge=1, le=100), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_least_active_users(session, days, limit, max_ts=max_ts)
