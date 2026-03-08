from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session, get_max_event_timestamp
from backend.app.queries import tools as q

router = APIRouter(prefix="/api/tools", tags=["Tools"])


@router.get("/usage") #Most used tools — Read, Edit, Bash, Write, etc. ranked

def tool_usage(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_tool_usage(session, days, max_ts=max_ts)


@router.get("/success-rates") #Tool success rate — which tools fail most

def tool_success_rates(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_tool_success_rates(session, days, max_ts=max_ts)


@router.get("/accept-reject") #Tool accept/reject rate — how often do users reject tool suggestions
def tool_accept_reject(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_tool_accept_reject(session, days, max_ts=max_ts)


@router.get("/rejection-sources") #Rejection source breakdown — config vs user_reject vs user_temporary

def rejection_sources(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_rejection_sources(session, days, max_ts=max_ts)


@router.get("/by-practice") #Tools by practice — do Frontend engineers use different tools than Backend?
def tools_by_practice(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_tools_by_practice(session, days, max_ts=max_ts)
