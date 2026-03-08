import streamlit as st
import requests

# Set the title of the page
st.title("Telemetry Events")

# Define the API endpoint for fetching telemetry events
API_URL = "http://localhost:8000/api/events"

# Fetch telemetry events from the backend
response = requests.get(API_URL)

if response.status_code == 200:
    events = response.json()
    # Display the events in a table
    st.write("### Telemetry Events")
    st.dataframe(events)
else:
    st.error("Failed to fetch telemetry events.")