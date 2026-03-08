import streamlit as st
import pandas as pd
import requests

# Set the title of the page
st.title("Claude Code Usage Analytics")

# Define the API endpoint for fetching telemetry data
API_URL = "http://localhost:8000/api/telemetry"

# Fetch telemetry data from the backend
@st.cache
def fetch_telemetry_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("Failed to fetch data from the API.")
        return pd.DataFrame()

# Load the telemetry data
telemetry_data = fetch_telemetry_data()

# Display the data in a table
if not telemetry_data.empty:
    st.subheader("Telemetry Data")
    st.dataframe(telemetry_data)

    # Add analytics options
    st.subheader("Analytics Options")
    if st.checkbox("Show Summary Statistics"):
        st.write(telemetry_data.describe())

    if st.checkbox("Show Correlation Matrix"):
        st.write(telemetry_data.corr())

    # Add more analytical views as needed
else:
    st.warning("No telemetry data available.")