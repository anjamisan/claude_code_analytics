from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session
from backend.app.queries import overview as q

router = APIRouter(prefix="/api/overview", tags=["Overview"])


@router.get("/summary")
def summary(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_summary_stats(session, days)


@router.get("/total-cost")
def total_cost(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_total_cost(session, days)


@router.get("/active-users")
def active_users(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_active_users(session, days)


@router.get("/cost-by-practice")
def cost_by_practice(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_cost_by_practice(session, days)


@router.get("/cost-by-level")
def cost_by_level(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_cost_by_level(session, days)


@router.get("/cost-by-location")
def cost_by_location(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_cost_by_location(session, days)


@router.get("/top-users")
def top_users(days: int = Query(30, ge=1, le=365), limit: int = Query(10, ge=1, le=100), session: Session = Depends(get_session)):
    return q.get_top_users_by_cost(session, days, limit)
