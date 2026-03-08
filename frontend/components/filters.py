from typing import List, Dict
import streamlit as st

def filter_events(events: List[Dict], filters: Dict) -> List[Dict]:
    """Filter events based on the provided filters."""
    filtered_events = events

    if filters.get("event_type"):
        filtered_events = [event for event in filtered_events if event["event_type"] == filters["event_type"]]

    if filters.get("date_range"):
        start_date, end_date = filters["date_range"]
        filtered_events = [
            event for event in filtered_events
            if start_date <= event["timestamp"] <= end_date
        ]

    return filtered_events

def render_filters() -> Dict:
    """Render filter components for user interaction."""
    st.sidebar.header("Filters")

    event_type = st.sidebar.selectbox("Event Type", options=["All", "api_request", "tool_decision", "tool_result", "api_error"])
    date_range = st.sidebar.date_input("Date Range", [])

    filters = {
        "event_type": event_type if event_type != "All" else None,
        "date_range": date_range if len(date_range) == 2 else None,
    }

    return filters