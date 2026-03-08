import streamlit as st

def main():
    st.title("Claude Code Usage Analytics Dashboard")

    st.header("Key Metrics")
    # Placeholder for key metrics
    st.metric(label="Total Users", value="0")
    st.metric(label="Total Sessions", value="0")
    st.metric(label="Total Events", value="0")

    st.header("Insights")
    # Placeholder for insights
    st.write("Insights will be displayed here.")

if __name__ == "__main__":
    main()