from typing import List
import streamlit as st
import pandas as pd
import altair as alt

def plot_line_chart(data: pd.DataFrame, x: str, y: str, title: str) -> None:
    chart = alt.Chart(data).mark_line().encode(
        x=x,
        y=y,
        tooltip=[x, y]
    ).properties(
        title=title
    )
    st.altair_chart(chart, use_container_width=True)

def plot_bar_chart(data: pd.DataFrame, x: str, y: str, title: str) -> None:
    chart = alt.Chart(data).mark_bar().encode(
        x=x,
        y=y,
        tooltip=[x, y]
    ).properties(
        title=title
    )
    st.altair_chart(chart, use_container_width=True)

def plot_histogram(data: pd.Series, title: str) -> None:
    chart = alt.Chart(data.reset_index()).mark_bar().encode(
        x=alt.X('index:O', title='Value'),
        y=alt.Y('value:Q', title='Count'),
        tooltip=['index', 'value']
    ).properties(
        title=title
    )
    st.altair_chart(chart, use_container_width=True)

def plot_charts(data: pd.DataFrame, chart_type: str, x: str, y: str) -> None:
    if chart_type == 'line':
        plot_line_chart(data, x, y, f'Line Chart of {y} over {x}')
    elif chart_type == 'bar':
        plot_bar_chart(data, x, y, f'Bar Chart of {y} by {x}')
    elif chart_type == 'histogram':
        plot_histogram(data[y], f'Histogram of {y}')
    else:
        st.error("Invalid chart type selected.")