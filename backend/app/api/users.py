from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from backend.app.database import get_session
from backend.app.queries import users as q

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/ranking")
def user_ranking(days: int = Query(30, ge=1, le=365), limit: int = Query(20, ge=1, le=100), session: Session = Depends(get_session)):
    return q.get_user_ranking(session, days, limit)


@router.get("/prompt-stats")
def prompt_stats(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_prompt_stats(session, days)


@router.get("/prompts-by-practice")
def prompts_by_practice(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_prompts_by_practice(session, days)


@router.get("/prompts-by-level")
def prompts_by_level(days: int = Query(30, ge=1, le=365), session: Session = Depends(get_session)):
    return q.get_prompts_by_level(session, days)


@router.get("/cost-breakdown")
def cost_breakdown(days: int = Query(30, ge=1, le=365), limit: int = Query(50, ge=1, le=200), session: Session = Depends(get_session)):
    return q.get_user_cost_breakdown(session, days, limit)
