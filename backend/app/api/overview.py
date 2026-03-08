from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session, get_max_event_timestamp
from backend.app.queries import overview as q
from backend.app.queries import users as users_q

router = APIRouter(prefix="/api/overview", tags=["Overview"])


@router.get("/summary") #Total events, sessions and users
def summary(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_summary_stats(session, days, max_ts=max_ts)


@router.get("/total-cost") #Total cost over time (daily/weekly trend line)
def total_cost(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_total_cost(session, days, max_ts=max_ts)


@router.get("/active-users") #Total active users over time
def active_users(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_active_users(session, days, max_ts=max_ts)


@router.get("/cost-by-practice") #Cost by practice
def cost_by_practice(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_cost_by_practice(session, days, max_ts=max_ts)


@router.get("/cost-by-level") #Cost by user level
def cost_by_level(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_cost_by_level(session, days, max_ts=max_ts)


@router.get("/cost-by-location") #Cost by location
def cost_by_location(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_cost_by_location(session, days, max_ts=max_ts)


@router.get("/top-users") #Top users by cost aka top spenders
def top_users(days: int = Query(60, ge=1, le=365), limit: int = Query(10, ge=1, le=100), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return users_q.get_user_cost_breakdown(session, days, limit, max_ts=max_ts)
