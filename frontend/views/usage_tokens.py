import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from api import fetch_df


def render():
    st.title("Usage & Tokens")

    days = st.sidebar.slider("Time window (days)", 1, 365, 60, key="usage_days")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # USAGE SECTION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.header("Usage Patterns")

    # ── Heatmap ────────────────────────────────────────────────
    st.subheader("Activity Heatmap (Hour × Day of Week)")
    df_heat = fetch_df("/usage/heatmap", {"days": days})
    if not df_heat.empty:
        day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        pivot = df_heat.pivot_table(index="day_of_week", columns="hour", values="event_count", fill_value=0)
        pivot = pivot.reindex(range(7), fill_value=0)
        pivot = pivot.reindex(columns=range(24), fill_value=0)

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=[f"{h}:00" for h in range(24)],
            y=day_labels,
            colorscale="Blues",
            hovertemplate="Day: %{y}<br>Hour: %{x}<br>Events: %{z}<extra></extra>",
        ))
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # ── Peak Hours + Distributions ─────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Peak Hours")
        df_peak = fetch_df("/usage/peak-hours", {"days": days})
        if not df_peak.empty:
            df_peak = df_peak.sort_values("hour")
            fig = px.bar(df_peak, x="hour", y="event_count",
                         labels={"hour": "Hour of Day", "event_count": "Events"})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Terminal Distribution")
        df_term = fetch_df("/usage/terminal-distribution", {"days": days})
        if not df_term.empty:
            fig = px.pie(df_term, values="event_count", names="terminal_type", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.subheader("OS Distribution")
        df_os = fetch_df("/usage/os-distribution", {"days": days})
        if not df_os.empty:
            df_os["label"] = df_os["os_type"] + " (" + df_os["host_arch"] + ")"
            fig = px.pie(df_os, values="event_count", names="label", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    # ── Model Popularity ───────────────────────────────────────
    st.subheader("Model Popularity")
    df_model = fetch_df("/usage/model-popularity", {"days": days})
    if not df_model.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.pie(df_model, values="usage_count", names="model", hole=0.4,
                         title="By Request Count")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = px.pie(df_model, values="total_cost", names="model", hole=0.4,
                         title="By Total Cost")
            st.plotly_chart(fig, use_container_width=True)

    # ── Sessions ───────────────────────────────────────────────
    st.subheader("Session Size Distribution")
    df_sess = fetch_df("/usage/sessions", {"days": days})
    if not df_sess.empty:
        fig = px.histogram(df_sess, x="event_count", nbins=30,
                           labels={"event_count": "Events per Session"})
        fig.update_layout(bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TOKENS SECTION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.header("Token Analytics")

    # ── Token Trends ───────────────────────────────────────────
    st.subheader("Daily Token Consumption")
    df_trends = fetch_df("/tokens/trends", {"days": days})
    if not df_trends.empty:
        df_trends["date"] = df_trends["date"].astype(str)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_trends["date"], y=df_trends["total_input"], name="Input", stackgroup="one"))
        fig.add_trace(go.Scatter(x=df_trends["date"], y=df_trends["total_output"], name="Output", stackgroup="one"))
        fig.add_trace(go.Scatter(x=df_trends["date"], y=df_trends["total_cache_read"], name="Cache Read", stackgroup="one"))
        fig.add_trace(go.Scatter(x=df_trends["date"], y=df_trends["total_cache_create"], name="Cache Create", stackgroup="one"))
        fig.update_layout(hovermode="x unified", yaxis_title="Tokens")
        st.plotly_chart(fig, use_container_width=True)

    # ── Cache Efficiency ───────────────────────────────────────
    st.subheader("Cache Efficiency Over Time")
    df_cache = fetch_df("/tokens/cache-efficiency", {"days": days})
    if not df_cache.empty:
        df_cache["date"] = df_cache["date"].astype(str)
        fig = px.line(df_cache, x="date", y="cache_hit_ratio",
                      labels={"date": "Date", "cache_hit_ratio": "Cache Hit Ratio (%)"})
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    # ── Input/Output Ratio ────────────────────────────────────
    st.subheader("Input / Output Token Ratio")
    df_ratio = fetch_df("/tokens/input-output-ratio", {"days": days})
    if not df_ratio.empty:
        df_ratio["date"] = df_ratio["date"].astype(str)
        fig = px.line(df_ratio, x="date", y="input_output_ratio",
                      labels={"date": "Date", "input_output_ratio": "Input:Output Ratio"})
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    # ── Cost by Model ──────────────────────────────────────────
    st.subheader("Average Cost per Request by Model")
    df_model_cost = fetch_df("/tokens/cost-by-model", {"days": days})
    if not df_model_cost.empty:
        fig = px.bar(df_model_cost, x="model", y="avg_cost",
                     text="num_requests",
                     labels={"model": "Model", "avg_cost": "Avg Cost (USD)", "num_requests": "Requests"})
        fig.update_traces(texttemplate="%{text} reqs", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    # ── Tokens by Practice & Level ─────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Tokens by Practice")
        df_tp = fetch_df("/tokens/by-practice", {"days": days})
        if not df_tp.empty:
            df_melted = df_tp.melt(id_vars="practice", value_vars=["total_input", "total_output"],
                                   var_name="type", value_name="tokens")
            fig = px.bar(df_melted, x="practice", y="tokens", color="type", barmode="group",
                         labels={"practice": "Practice", "tokens": "Tokens"})
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Tokens by Level")
        df_tl = fetch_df("/tokens/by-level", {"days": days})
        if not df_tl.empty:
            df_melted = df_tl.melt(id_vars="level", value_vars=["total_input", "total_output"],
                                   var_name="type", value_name="tokens")
            fig = px.bar(df_melted, x="level", y="tokens", color="type", barmode="group",
                         labels={"level": "Level", "tokens": "Tokens"})
            st.plotly_chart(fig, use_container_width=True)
