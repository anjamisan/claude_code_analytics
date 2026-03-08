from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session, get_max_event_timestamp
from backend.app.queries import tokens as q

router = APIRouter(prefix="/api/tokens", tags=["Tokens"])


@router.get("/trends") #Token consumption trends — daily input/output/cache tokens over time
def token_trends(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_token_trends(session, days, max_ts=max_ts)


@router.get("/by-practice") #Token usage by practice — which teams consume the most tokens
def tokens_by_practice(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_tokens_by_practice(session, days, max_ts=max_ts)


@router.get("/by-level") #Token usage by level (L1-L10) — do seniors use more?
def tokens_by_level(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_tokens_by_level(session, days, max_ts=max_ts)


@router.get("/cache-efficiency") #Cache hit ratio — cache_read_tokens vs cache_creation_tokens (efficiency metric)
def cache_efficiency(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_cache_efficiency(session, days, max_ts=max_ts)


@router.get("/cost-by-model") #Average cost per request by model — cost efficiency comparison
def cost_by_model(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_avg_cost_by_model(session, days, max_ts=max_ts)


@router.get("/input-output-ratio") #Token input vs output ratio — how much context vs generated code
def input_output_ratio(days: int = Query(60, ge=1, le=365), session: Session = Depends(get_session)):
    max_ts = get_max_event_timestamp(session)
    return q.get_input_output_ratio(session, days, max_ts=max_ts)
