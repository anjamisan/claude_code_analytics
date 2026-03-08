import streamlit as st
import plotly.express as px
import pandas as pd
from api import fetch_df


def render():
    st.title("Tools")

    days = st.sidebar.slider("Time window (days)", 1, 365, 60, key="tools_days")

    # ── Tool Usage Ranking ─────────────────────────────────────
    st.subheader("Most Used Tools")
    df_usage = fetch_df("/tools/usage", {"days": days})
    if not df_usage.empty:
        fig = px.bar(df_usage, x="usage_count", y="tool_name", orientation="h",
                     labels={"usage_count": "Usage Count", "tool_name": "Tool"})
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Success Rates + Accept/Reject ─────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tool Success Rates")
        df_sr = fetch_df("/tools/success-rates", {"days": days})
        if not df_sr.empty:
            fig = px.bar(df_sr, x="success_rate", y="tool_name", orientation="h",
                         text="success_rate",
                         labels={"success_rate": "Success Rate (%)", "tool_name": "Tool"})
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_range=[0, 105])
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Accept vs Reject by Tool")
        df_ar = fetch_df("/tools/accept-reject", {"days": days})
        if not df_ar.empty:
            fig = px.bar(df_ar, x="count", y="tool_name", color="decision",
                         orientation="h", barmode="stack",
                         labels={"count": "Count", "tool_name": "Tool", "decision": "Decision"})
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Rejection Sources + Tools by Practice ─────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Rejection Sources")
        df_rej = fetch_df("/tools/rejection-sources", {"days": days})
        if not df_rej.empty:
            fig = px.pie(df_rej, values="count", names="source", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Tool Usage by Practice")
        df_bp = fetch_df("/tools/by-practice", {"days": days})
        if not df_bp.empty:
            # Show top 8 tools to keep chart readable
            top_tools = df_bp.groupby("tool_name")["usage_count"].sum().nlargest(8).index
            df_bp = df_bp[df_bp["tool_name"].isin(top_tools)]
            fig = px.bar(df_bp, x="practice", y="usage_count", color="tool_name",
                         barmode="group",
                         labels={"practice": "Practice", "usage_count": "Count", "tool_name": "Tool"})
            st.plotly_chart(fig, use_container_width=True)
