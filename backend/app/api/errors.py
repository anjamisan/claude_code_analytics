from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session, get_max_event_timestamp
from backend.app.queries import errors as q

router = APIRouter(prefix="/api/errors", tags=["Errors"])


@router.get("/rate") #Error rate over time — are errors increasing?
def error_rate(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_error_rate(session, days, max_ts=max_ts)


@router.get("/by-status") #Errors by status code — 429 (rate limit), 500 (server), etc.
def errors_by_status(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_errors_by_status(session, days, max_ts=max_ts)


@router.get("/by-model") #Errors by model — which models are least reliable
def errors_by_model(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_errors_by_model(session, days, max_ts=max_ts)


@router.get("/retries") #Retry patterns — distribution of attempt counts
def retry_distribution(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_retry_distribution(session, days, max_ts=max_ts)


@router.get("/top-messages") #Error messages — top error messages (grouped)
def top_error_messages(days: int = Query(60, ge=1, le=365), limit: int = Query(10, ge=1, le=50), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_top_error_messages(session, days, limit, max_ts=max_ts)
