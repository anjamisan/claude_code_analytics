import streamlit as st
import importlib

st.set_page_config(
    page_title="Claude Code Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000/api"

PAGES = {
    "🏠 Overview": "views.overview",
    "📈 Usage & Tokens": "views.usage_tokens",
    "🔮 Predictions": "views.predictions",
    "🔧 Tools": "views.tools",
    "⚠️ Errors": "views.errors",
    "👥 Users": "views.users",
}

st.sidebar.title("Claude Code Analytics")
selection = st.sidebar.radio("Navigate", list(PAGES.keys()))

module = importlib.import_module(PAGES[selection])
module.render()