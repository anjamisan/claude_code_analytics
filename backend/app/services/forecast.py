from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _to_dense_daily_series(points: List[Tuple[date, float]], fill_value: float = 0.0) -> List[Tuple[date, float]]:
    if not points:
        return []

    points = sorted(points, key=lambda x: x[0])
    value_by_date = {d: float(v) for d, v in points}
    current = points[0][0]
    end = points[-1][0]

    dense: List[Tuple[date, float]] = []
    while current <= end:
        dense.append((current, value_by_date.get(current, fill_value)))
        current += timedelta(days=1)
    return dense


def _linear_forecast(values: List[float], horizon: int, non_negative: bool = True) -> Tuple[List[float], float]:
    n = len(values)
    if n == 0:
        return [0.0] * horizon, 0.0

    if n == 1:
        pred = [values[0]] * horizon
        if non_negative:
            pred = [max(0.0, p) for p in pred]
        return pred, 0.0

    x_vals = list(range(n))
    sum_x = float(sum(x_vals))
    sum_y = float(sum(values))
    sum_xy = float(sum(x * y for x, y in zip(x_vals, values)))
    sum_x2 = float(sum(x * x for x in x_vals))

    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        slope = 0.0
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    in_sample = [intercept + slope * x for x in x_vals]
    residuals = [actual - fitted for actual, fitted in zip(values, in_sample)]
    residual_var = sum(r * r for r in residuals) / max(1, (n - 2))
    residual_std = residual_var ** 0.5

    future = [intercept + slope * (n + i) for i in range(horizon)]
    if non_negative:
        future = [max(0.0, p) for p in future]

    return future, residual_std


def _evaluate(values: List[float], holdout: int, non_negative: bool = True) -> Dict[str, float] | None:
    if len(values) < max(8, holdout + 3):
        return None

    train = values[:-holdout]
    actual = values[-holdout:]
    pred, _ = _linear_forecast(train, holdout, non_negative=non_negative)

    abs_errors = [abs(a - p) for a, p in zip(actual, pred)]
    mae = sum(abs_errors) / len(abs_errors)

    ape = [abs((a - p) / a) for a, p in zip(actual, pred) if a != 0]
    mape = (sum(ape) / len(ape) * 100.0) if ape else None

    return {
        "mae": round(mae, 4),
        "mape": round(mape, 4) if mape is not None else None,
        "holdout_days": holdout,
    }


def _build_backtest_univariate(
    dates: List[date], values: List[float], holdout: int, non_negative: bool = True
) -> List[Dict]:
    if len(values) < max(8, holdout + 3):
        return []

    train = values[:-holdout]
    actual = values[-holdout:]
    actual_dates = dates[-holdout:]
    predicted, _ = _linear_forecast(train, holdout, non_negative=non_negative)

    rows: List[Dict] = []
    for d, a, p in zip(actual_dates, actual, predicted):
        rows.append(
            {
                "date": d.isoformat(),
                "actual": round(a, 6),
                "predicted": round(p, 6),
            }
        )
    return rows


def forecast_univariate_daily(
    rows: List[Dict],
    value_key: str,
    horizon_days: int,
    non_negative: bool = True,
) -> Dict:
    points: List[Tuple[date, float]] = [(_parse_date(r["date"]), float(r[value_key])) for r in rows]
    dense = _to_dense_daily_series(points, fill_value=0.0)

    dates = [d for d, _ in dense]
    values = [v for _, v in dense]

    preds, residual_std = _linear_forecast(values, horizon_days, non_negative=non_negative)
    holdout = min(14, max(3, len(values) // 5))
    evaluation = _evaluate(values, holdout=holdout, non_negative=non_negative)
    backtest = _build_backtest_univariate(dates, values, holdout=holdout, non_negative=non_negative)

    historical = [{"date": d.isoformat(), "value": round(v, 6)} for d, v in dense]

    z = 1.96
    forecast = []
    last_date = dates[-1]
    for i, p in enumerate(preds, start=1):
        lower = p - z * residual_std
        upper = p + z * residual_std
        if non_negative:
            lower = max(0.0, lower)
        forecast.append({
            "date": (last_date + timedelta(days=i)).isoformat(),
            "predicted": round(p, 6),
            "lower": round(lower, 6),
            "upper": round(upper, 6),
        })

    return {
        "model_type": "linear_trend_baseline",
        "historical": historical,
        "backtest": backtest,
        "forecast": forecast,
        "evaluation": evaluation,
    }


def forecast_multivariate_daily(
    rows: List[Dict],
    value_keys: List[str],
    horizon_days: int,
) -> Dict:
    date_points = sorted({_parse_date(r["date"]) for r in rows})
    if not date_points:
        return {
            "model_type": "linear_trend_baseline",
            "historical": [],
            "forecast": [],
            "evaluation": {},
        }

    by_date = {_parse_date(r["date"]): r for r in rows}
    dense_rows: List[Dict] = []
    current = date_points[0]
    end = date_points[-1]
    while current <= end:
        src = by_date.get(current, {})
        item = {"date": current.isoformat()}
        for key in value_keys:
            item[key] = float(src.get(key, 0.0))
        dense_rows.append(item)
        current += timedelta(days=1)

    historical = dense_rows
    evaluation: Dict[str, Dict | None] = {}
    backtest: Dict[str, List[Dict]] = {}

    forecasts_by_metric: Dict[str, List[Dict]] = {}
    last_date = _parse_date(dense_rows[-1]["date"])

    for key in value_keys:
        series = [float(r[key]) for r in dense_rows]
        preds, residual_std = _linear_forecast(series, horizon_days, non_negative=True)
        holdout = min(14, max(3, len(series) // 5))
        evaluation[key] = _evaluate(series, holdout=holdout, non_negative=True)
        backtest[key] = _build_backtest_univariate(
            dates=[_parse_date(r["date"]) for r in dense_rows],
            values=series,
            holdout=holdout,
            non_negative=True,
        )

        z = 1.96
        forecasts_by_metric[key] = []
        for i, p in enumerate(preds, start=1):
            lower = max(0.0, p - z * residual_std)
            upper = p + z * residual_std
            forecasts_by_metric[key].append({
                "date": (last_date + timedelta(days=i)).isoformat(),
                "predicted": round(p, 6),
                "lower": round(lower, 6),
                "upper": round(upper, 6),
            })

    forecast: List[Dict] = []
    for i in range(horizon_days):
        row = {"date": forecasts_by_metric[value_keys[0]][i]["date"]}
        for key in value_keys:
            row[f"{key}_predicted"] = forecasts_by_metric[key][i]["predicted"]
            row[f"{key}_lower"] = forecasts_by_metric[key][i]["lower"]
            row[f"{key}_upper"] = forecasts_by_metric[key][i]["upper"]
        forecast.append(row)

    return {
        "model_type": "linear_trend_baseline",
        "historical": historical,
        "backtest": backtest,
        "forecast": forecast,
        "evaluation": evaluation,
    }
