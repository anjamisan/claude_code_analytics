from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session, get_max_event_timestamp
from backend.app.queries import usage as q

router = APIRouter(prefix="/api/usage", tags=["Usage"])


@router.get("/peak-hours") #Peak usage hours 
def peak_hours(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_peak_hours(session, days, max_ts=max_ts)


@router.get("/heatmap") #Heatmap of events by hour-of-day × day-of-week
def usage_heatmap(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_usage_heatmap(session, days, max_ts=max_ts)


@router.get("/model-popularity") #Model popularity — pie/bar chart of which Claude models are used most
def model_popularity(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_model_popularity(session, days, max_ts=max_ts)


@router.get("/terminal-distribution") #Terminal type distribution — VSCode vs PyCharm vs terminal etc.
def terminal_distribution(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_terminal_distribution(session, days, max_ts=max_ts)


@router.get("/sessions") #Events per session — how active are sessions
def events_per_session(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_events_per_session(session, days, max_ts=max_ts)


@router.get("/os-distribution") #OS distribution — which operating systems are users on
def os_distribution(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_os_distribution(session, days, max_ts=max_ts)
