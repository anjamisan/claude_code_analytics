import streamlit as st
import plotly.express as px
from api import fetch, fetch_df


def render():
    st.title("Users")

    days = st.sidebar.slider("Time window (days)", 1, 365, 60, key="users_days")

    # ── Prompt Stats KPIs ──────────────────────────────────────
    stats = fetch("/users/prompt-stats", {"days": days})
    if stats:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Prompts", f"{stats.get('total_prompts', 0):,}")
        c2.metric("Avg Length", f"{stats.get('avg_length', 0):,.0f} chars")
        c3.metric("Median Length", f"{stats.get('median_length', 0):,.0f} chars")
        c4.metric("Min Length", f"{stats.get('min_length', 0):,} chars")
        c5.metric("Max Length", f"{stats.get('max_length', 0):,} chars")

    st.divider()

    # ── Most Active + Least Active ────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Most Active Users")
        df_top = fetch_df("/users/ranking", {"days": days, "limit": 15})
        if not df_top.empty:
            fig = px.bar(df_top, x="total_events", y="full_name", orientation="h",
                         color="practice",
                         labels={"total_events": "Events", "full_name": "User"})
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Least Active Users")
        df_bot = fetch_df("/users/least-active", {"days": days, "limit": 15})
        if not df_bot.empty:
            fig = px.bar(df_bot, x="total_events", y="full_name", orientation="h",
                         color="practice",
                         labels={"total_events": "Events", "full_name": "User"})
            fig.update_layout(yaxis={"categoryorder": "total descending"})
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Cost Breakdown ─────────────────────────────────────────
    st.subheader("User Cost Breakdown")
    df_cost = fetch_df("/users/cost-breakdown", {"days": days, "limit": 30})
    if not df_cost.empty:
        fig = px.treemap(df_cost, path=["practice", "full_name"], values="total_cost",
                         color="total_cost", color_continuous_scale="Blues",
                         labels={"total_cost": "Cost (USD)"})
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Prompts by Practice + Level ───────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Prompts by Practice")
        df_pp = fetch_df("/users/prompts-by-practice", {"days": days})
        if not df_pp.empty:
            fig = px.bar(df_pp, x="practice", y="total_prompts",
                         text="avg_length",
                         labels={"practice": "Practice", "total_prompts": "Total Prompts"})
            fig.update_traces(texttemplate="avg %{text:.0f} chars", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Prompts by Level")
        df_pl = fetch_df("/users/prompts-by-level", {"days": days})
        if not df_pl.empty:
            fig = px.bar(df_pl, x="level", y="total_prompts",
                         text="avg_length",
                         labels={"level": "Level", "total_prompts": "Total Prompts"})
            fig.update_traces(texttemplate="avg %{text:.0f} chars", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
