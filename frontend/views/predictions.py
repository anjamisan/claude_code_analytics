import pandas as pd
import plotly.express as px
import streamlit as st

from api import fetch


def _split_univariate(result: dict):
    hist = pd.DataFrame(result.get("historical", []))
    backtest = pd.DataFrame(result.get("backtest", []))
    fut = pd.DataFrame(result.get("forecast", []))
    if not hist.empty:
        hist["date"] = pd.to_datetime(hist["date"], errors="coerce")
    if not backtest.empty:
        backtest["date"] = pd.to_datetime(backtest["date"], errors="coerce")
    if not fut.empty:
        fut["date"] = pd.to_datetime(fut["date"], errors="coerce")
    return hist, backtest, fut


def _render_univariate_evaluation(evaluation: dict | None, label: str):
    if not evaluation:
        return
    st.caption(
        f"{label} model quality - MAE: {evaluation.get('mae', 0):,.4f} | "
        f"MAPE: {evaluation.get('mape', 0):,.2f}% | "
        f"Holdout: {evaluation.get('holdout_days', 0)} days"
    )


def _render_multivariate_evaluation(evaluation: dict | None):
    if not evaluation:
        return
    rows = []
    for metric, stats in evaluation.items():
        if not stats:
            continue
        rows.append({
            "metric": metric,
            "mae": stats.get("mae"),
            "mape_percent": stats.get("mape"),
            "holdout_days": stats.get("holdout_days"),
        })
    if not rows:
        return
    df_eval = pd.DataFrame(rows)
    st.caption("Token forecast model quality")
    st.dataframe(df_eval, use_container_width=True, hide_index=True)


def render():
    st.title("Predictions")

    days = st.sidebar.slider("Training window (days)", 14, 60, 60, key="pred_days")
    horizon = st.sidebar.slider("Forecast horizon (days)", 1, 60, 14, key="pred_horizon")

    st.caption("Baseline model: linear trend extrapolation with 95% residual interval.")

    # Total cost forecast
    st.subheader("Forecast: Total Cost")
    total_cost = fetch("/predictions/total-cost", {"days": days, "horizon": horizon})
    if isinstance(total_cost, dict) and total_cost.get("historical"):
        hist, backtest, fut = _split_univariate(total_cost)
        fig = px.line(hist, x="date", y="value", labels={"value": "Cost (USD)", "date": "Date"})
        if not backtest.empty:
            fig.add_scatter(x=backtest["date"], y=backtest["actual"], mode="lines", name="Holdout Actual")
            fig.add_scatter(
                x=backtest["date"],
                y=backtest["predicted"],
                mode="lines",
                name="Holdout Predicted",
                line={"dash": "dash"},
            )
        if not fut.empty:
            fig.add_scatter(x=fut["date"], y=fut["predicted"], mode="lines", name="Forecast")
            fig.add_scatter(x=fut["date"], y=fut["lower"], mode="lines", name="Lower", line={"dash": "dot"})
            fig.add_scatter(x=fut["date"], y=fut["upper"], mode="lines", name="Upper", line={"dash": "dot"})
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        _render_univariate_evaluation(total_cost.get("evaluation"), "Total cost")

    # Token trends forecast
    st.subheader("Forecast: Token Trends")
    token_trends = fetch("/predictions/token-trends", {"days": days, "horizon": horizon})
    if isinstance(token_trends, dict) and token_trends.get("historical"):
        hist = pd.DataFrame(token_trends.get("historical", []))
        backtest = token_trends.get("backtest", {}) or {}
        fut = pd.DataFrame(token_trends.get("forecast", []))

        if not hist.empty:
            hist["date"] = pd.to_datetime(hist["date"], errors="coerce")
            fig = px.line(
                hist,
                x="date",
                y=["total_input", "total_output"],
                labels={"value": "Tokens", "date": "Date", "variable": "Metric"},
            )
            if not fut.empty:
                fut["date"] = pd.to_datetime(fut["date"], errors="coerce")
                fig.add_scatter(x=fut["date"], y=fut["total_input_predicted"], mode="lines", name="Forecast Input")
                fig.add_scatter(x=fut["date"], y=fut["total_output_predicted"], mode="lines", name="Forecast Output")
            bt_input = pd.DataFrame(backtest.get("total_input", []))
            bt_output = pd.DataFrame(backtest.get("total_output", []))
            if not bt_input.empty:
                bt_input["date"] = pd.to_datetime(bt_input["date"], errors="coerce")
                fig.add_scatter(
                    x=bt_input["date"],
                    y=bt_input["actual"],
                    mode="lines",
                    name="Holdout Input Actual",
                )
                fig.add_scatter(
                    x=bt_input["date"],
                    y=bt_input["predicted"],
                    mode="lines",
                    name="Holdout Input Predicted",
                    line={"dash": "dash"},
                )
            if not bt_output.empty:
                bt_output["date"] = pd.to_datetime(bt_output["date"], errors="coerce")
                fig.add_scatter(
                    x=bt_output["date"],
                    y=bt_output["actual"],
                    mode="lines",
                    name="Holdout Output Actual",
                )
                fig.add_scatter(
                    x=bt_output["date"],
                    y=bt_output["predicted"],
                    mode="lines",
                    name="Holdout Output Predicted",
                    line={"dash": "dash"},
                )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            _render_multivariate_evaluation(token_trends.get("evaluation"))

    # Input/output ratio forecast
    st.subheader("Forecast: Input/Output Ratio")
    ratio = fetch("/predictions/input-output-ratio", {"days": days, "horizon": horizon})
    if isinstance(ratio, dict) and ratio.get("historical"):
        hist, backtest, fut = _split_univariate(ratio)
        fig = px.line(hist, x="date", y="value", labels={"value": "Input/Output Ratio", "date": "Date"})
        if not backtest.empty:
            fig.add_scatter(x=backtest["date"], y=backtest["actual"], mode="lines", name="Holdout Actual")
            fig.add_scatter(
                x=backtest["date"],
                y=backtest["predicted"],
                mode="lines",
                name="Holdout Predicted",
                line={"dash": "dash"},
            )
        if not fut.empty:
            fig.add_scatter(x=fut["date"], y=fut["predicted"], mode="lines", name="Forecast")
            fig.add_scatter(x=fut["date"], y=fut["lower"], mode="lines", name="Lower", line={"dash": "dot"})
            fig.add_scatter(x=fut["date"], y=fut["upper"], mode="lines", name="Upper", line={"dash": "dot"})
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        _render_univariate_evaluation(ratio.get("evaluation"), "Input/output ratio")
