import streamlit as st
import plotly.express as px
import pandas as pd
from api import fetch, fetch_df


def render():
    st.title("Overview")

    days = st.sidebar.slider("Time window (days)", 1, 365, 60, key="overview_days")

    # ── KPI Cards ──────────────────────────────────────────────
    stats = fetch("/overview/summary", {"days": days})
    if stats:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Events", f"{stats.get('total_events', 0):,}")
        c2.metric("Sessions", f"{stats.get('total_sessions', 0):,}")
        c3.metric("Active Users", f"{stats.get('total_users', 0):,}")
        c4.metric("Total Cost", f"${stats.get('total_cost', 0):,.2f}")

    st.divider()

    # ── Cost Over Time ─────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Cost Over Time")
        df_cost = fetch_df("/overview/total-cost", {"days": days})
        if not df_cost.empty:
            # Ensure Plotly receives a real time series (not categorical/string axes).
            df_cost["date"] = pd.to_datetime(df_cost["date"], errors="coerce")
            df_cost["total_cost"] = pd.to_numeric(df_cost["total_cost"], errors="coerce")
            df_cost = df_cost.dropna(subset=["date", "total_cost"]).sort_values("date")
            fig = px.line(
                df_cost,
                x="date",
                y="total_cost",
                markers=True,
                labels={"date": "Date", "total_cost": "Cost (USD)"},
            )
            fig.update_layout(hovermode="x unified")
            fig.update_yaxes(tickprefix="$")
            st.plotly_chart(fig, use_container_width=True)

    # ── Active Users Over Time ─────────────────────────────────
    with col_right:
        st.subheader("Active Users Over Time")
        df_users = fetch_df("/overview/active-users", {"days": days})
        if not df_users.empty:
            df_users["date"] = df_users["date"].astype(str)
            fig = px.line(df_users, x="date", y="active_users", labels={"date": "Date", "active_users": "Users"})
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Cost Breakdown ─────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Cost by Practice")
        df = fetch_df("/overview/cost-by-practice", {"days": days})
        if not df.empty:
            fig = px.bar(df, x="total_cost", y="practice", orientation="h",
                         labels={"total_cost": "Cost (USD)", "practice": "Practice"},
                         color="practice")
            fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Cost by Level")
        df = fetch_df("/overview/cost-by-level", {"days": days})
        if not df.empty:
            fig = px.bar(df, x="level", y="total_cost",
                         labels={"total_cost": "Cost (USD)", "level": "Level"},
                         color="level")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.subheader("Cost by Location")
        df = fetch_df("/overview/cost-by-location", {"days": days})
        if not df.empty:
            fig = px.pie(df, values="total_cost", names="location", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Top Users ──────────────────────────────────────────────
    st.subheader("Top Users by Cost")
    df_top = fetch_df("/overview/top-users", {"days": days, "limit": 10})
    if not df_top.empty:
        fig = px.bar(df_top, x="total_cost", y="full_name", orientation="h",
                     color="practice",
                     labels={"total_cost": "Cost (USD)", "full_name": "User"})
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
