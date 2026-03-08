from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session
from backend.app.queries import tools as q

router = APIRouter(prefix="/api/tools", tags=["Tools"])


@router.get("/usage")
def tool_usage(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_tool_usage(session, days)


@router.get("/success-rates")
def tool_success_rates(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_tool_success_rates(session, days)


@router.get("/accept-reject")
def tool_accept_reject(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_tool_accept_reject(session, days)


@router.get("/rejection-sources")
def rejection_sources(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_rejection_sources(session, days)


@router.get("/by-practice")
def tools_by_practice(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_tools_by_practice(session, days)
