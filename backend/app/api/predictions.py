from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from backend.app.database import get_session, get_max_event_timestamp
from backend.app.queries import overview as overview_q
from backend.app.queries import tokens as tokens_q
from backend.app.services.forecast import forecast_univariate_daily, forecast_multivariate_daily

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.get("/total-cost")
def predict_total_cost(
    days: int = Query(90, ge=14, le=365),
    horizon: int = Query(14, ge=1, le=60),
    session: Session = Depends(get_session),
):
    max_ts = get_max_event_timestamp(session)
    rows = overview_q.get_total_cost(session, days, max_ts=max_ts)
    result = forecast_univariate_daily(rows, value_key="total_cost", horizon_days=horizon, non_negative=True)
    result.update({
        "metric": "total_cost",
        "train_window_days": days,
        "horizon_days": horizon,
    })
    return result


@router.get("/token-trends")
def predict_token_trends(
    days: int = Query(90, ge=14, le=365),
    horizon: int = Query(14, ge=1, le=60),
    session: Session = Depends(get_session),
):
    max_ts = get_max_event_timestamp(session)
    rows = tokens_q.get_token_trends(session, days, max_ts=max_ts)
    result = forecast_multivariate_daily(
        rows,
        value_keys=["total_input", "total_output", "total_cache_read", "total_cache_create"],
        horizon_days=horizon,
    )
    result.update({
        "metric": "token_trends",
        "train_window_days": days,
        "horizon_days": horizon,
    })
    return result


@router.get("/input-output-ratio")
def predict_input_output_ratio(
    days: int = Query(90, ge=14, le=365),
    horizon: int = Query(14, ge=1, le=60),
    session: Session = Depends(get_session),
):
    max_ts = get_max_event_timestamp(session)
    rows = tokens_q.get_input_output_ratio(session, days, max_ts=max_ts)
    result = forecast_univariate_daily(rows, value_key="input_output_ratio", horizon_days=horizon, non_negative=True)
    result.update({
        "metric": "input_output_ratio",
        "train_window_days": days,
        "horizon_days": horizon,
    })
    return result
