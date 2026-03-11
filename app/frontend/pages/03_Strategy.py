import streamlit as st
from app.frontend.components.sidebar import show_sidebar
from app.frontend.utils.auth import is_logged_in
from app.frontend.utils.api_client import api_client
from app.frontend.utils.ui import apply_custom_style, show_header

st.set_page_config(page_title="Strategy - DevApply", page_icon="🎯", layout="wide")
apply_custom_style()


def show_strategy_page():
    if not is_logged_in():
        st.switch_page("pages/01_Login.py")

    show_sidebar()
    show_header("🎯 Strategy Configuration", "Tune your autonomous job search parameters.")

    # Load existing strategies
    response = api_client.get("/api/strategies/")
    strategies = response.json() if response and response.status_code == 200 else []

    if strategies:
        st.subheader("Current Strategies")
        for s in strategies:
            with st.expander(f"{s['name']} {'(Active)' if s.get('is_active') else ''}"):
                st.write(f"**Target Titles:** {', '.join(s.get('target_job_titles', []))}")
                st.write(f"**Location:** {', '.join(s.get('location_preferences', []))}")
                if st.button("Activate", key=f"act_{s['id']}"):
                    api_client.post(f"/api/strategies/{s['id']}/activate")
                    st.rerun()

    st.divider()
    st.subheader("➕ Create New Strategy")
    with st.form("strategy_form"):
        name = st.text_input("Strategy Name", placeholder="e.g., Python Backend Dev")
        job_titles = st.multiselect(
            "Target Job Titles",
            ["Python Developer", "Full Stack Engineer", "AI Engineer", "Data Scientist", "DevOps Engineer"],
        )
        
        col1, col2 = st.columns(2)
        with col1:
            job_types = st.multiselect(
                "Job Types", ["Full-time", "Contract", "Freelance", "Internship"]
            )
        with col2:
            location = st.multiselect("Location", ["Remote", "On-site", "Hybrid"])

        submitted = st.form_submit_button("Save Strategy")
        if submitted:
            strategy_data = {
                "name": name,
                "target_job_titles": job_titles,
                "job_types": job_types,
                "location_preferences": location,
                "is_active": True
            }
            res = api_client.post("/api/strategies/", data=strategy_data)
            if res and res.status_code == 200:
                st.success(f"Strategy '{name}' saved and activated!")
                st.rerun()
            else:
                st.error("Failed to save strategy.")


if __name__ == "__main__":
    show_strategy_page()
