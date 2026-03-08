from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session
from backend.app.queries import errors as q

router = APIRouter(prefix="/api/errors", tags=["Errors"])


@router.get("/rate")
def error_rate(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_error_rate(session, days)


@router.get("/by-status")
def errors_by_status(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_errors_by_status(session, days)


@router.get("/by-model")
def errors_by_model(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_errors_by_model(session, days)


@router.get("/retries")
def retry_distribution(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_retry_distribution(session, days)


@router.get("/top-messages")
def top_error_messages(days: int = Query(30, ge=1, le=365), limit: int = Query(10, ge=1, le=50), session: Session = Depends(get_session)):
    return q.get_top_error_messages(session, days, limit)
