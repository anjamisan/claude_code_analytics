import streamlit as st
import requests
import pandas as pd
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")


def fetch(endpoint: str, params: dict | None = None) -> list | dict:
    """Fetch data from the FastAPI backend. Returns parsed JSON."""
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        st.error("Cannot connect to the backend API. Is the FastAPI server running on port 8000?")
        return []
    except requests.HTTPError as e:
        st.error(f"API error: {e.response.status_code}")
        return []


def fetch_df(endpoint: str, params: dict | None = None) -> pd.DataFrame:
    """Fetch data and return as a DataFrame."""
    data = fetch(endpoint, params)
    if not data:
        return pd.DataFrame()
    if isinstance(data, dict):
        return pd.DataFrame([data])
    return pd.DataFrame(data)
