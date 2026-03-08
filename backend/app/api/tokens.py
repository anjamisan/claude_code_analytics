from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session
from backend.app.queries import tokens as q

router = APIRouter(prefix="/api/tokens", tags=["Tokens"])


@router.get("/trends")
def token_trends(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_token_trends(session, days)


@router.get("/by-practice")
def tokens_by_practice(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_tokens_by_practice(session, days)


@router.get("/by-level")
def tokens_by_level(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_tokens_by_level(session, days)


@router.get("/cache-efficiency")
def cache_efficiency(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_cache_efficiency(session, days)


@router.get("/cost-by-model")
def cost_by_model(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_avg_cost_by_model(session, days)
