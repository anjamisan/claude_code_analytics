from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session
from backend.app.queries import usage as q

router = APIRouter(prefix="/api/usage", tags=["Usage"])


@router.get("/peak-hours")
def peak_hours(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_peak_hours(session, days)


@router.get("/heatmap")
def usage_heatmap(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_usage_heatmap(session, days)


@router.get("/model-popularity")
def model_popularity(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_model_popularity(session, days)


@router.get("/terminal-distribution")
def terminal_distribution(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_terminal_distribution(session, days)


@router.get("/sessions")
def events_per_session(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_events_per_session(session, days)


@router.get("/os-distribution")
def os_distribution(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_os_distribution(session, days)
