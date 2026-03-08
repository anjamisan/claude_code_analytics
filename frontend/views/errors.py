import streamlit as st
import plotly.express as px
from api import fetch_df


def render():
    st.title("Errors")

    days = st.sidebar.slider("Time window (days)", 1, 365, 60, key="errors_days")

    # ── Error Rate Over Time ──────────────────────────────────
    st.subheader("Error Rate Over Time")
    df_rate = fetch_df("/errors/rate", {"days": days})
    if not df_rate.empty:
        df_rate["date"] = df_rate["date"].astype(str)
        fig = px.line(df_rate, x="date", y="error_count",
                      labels={"date": "Date", "error_count": "Errors"})
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── By Status Code + By Model ─────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Errors by Status Code")
        df_status = fetch_df("/errors/by-status", {"days": days})
        if not df_status.empty:
            df_status["status_code"] = df_status["status_code"].astype(str)
            fig = px.bar(df_status, x="status_code", y="count",
                         color="status_code",
                         labels={"status_code": "HTTP Status", "count": "Count"})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Errors by Model")
        df_model = fetch_df("/errors/by-model", {"days": days})
        if not df_model.empty:
            fig = px.bar(df_model, x="model", y="count",
                         color="model",
                         labels={"model": "Model", "count": "Count"})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Retry Distribution ────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Retry Attempt Distribution")
        df_retry = fetch_df("/errors/retries", {"days": days})
        if not df_retry.empty:
            df_retry["attempt"] = df_retry["attempt"].astype(str)
            fig = px.bar(df_retry, x="attempt", y="count",
                         labels={"attempt": "Attempt #", "count": "Count"})
            st.plotly_chart(fig, use_container_width=True)

    # ── Top Error Messages ────────────────────────────────────
    with col4:
        st.subheader("Top Error Messages")
        df_msgs = fetch_df("/errors/top-messages", {"days": days, "limit": 10})
        if not df_msgs.empty:
            fig = px.bar(df_msgs, x="count", y="error_message", orientation="h",
                         labels={"count": "Count", "error_message": "Message"})
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
