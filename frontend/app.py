from fastapi import FastAPI
import streamlit as st

# Initialize the FastAPI application
app = FastAPI()

# Streamlit application layout
def main():
    st.title("Claude Code Usage Analytics")
    st.sidebar.title("Navigation")
    
    # Sidebar navigation
    page = st.sidebar.selectbox("Select a page", ["Dashboard", "Events", "Analytics"])
    
    if page == "Dashboard":
        st.write("Welcome to the Dashboard!")
        # Add dashboard components here
    elif page == "Events":
        st.write("Explore Telemetry Events")
        # Add events display components here
    elif page == "Analytics":
        st.write("Analytics Insights")
        # Add analytics components here

if __name__ == "__main__":
    main()