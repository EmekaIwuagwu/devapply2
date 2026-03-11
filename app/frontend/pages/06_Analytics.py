import streamlit as st
import plotly.express as px
import pandas as pd
from app.frontend.components.sidebar import show_sidebar
from app.frontend.utils.auth import is_logged_in
from app.frontend.utils.api_client import api_client
from app.frontend.utils.ui import apply_custom_style, show_header

st.set_page_config(page_title="Analytics - DevApply", page_icon="📈", layout="wide")
apply_custom_style()


def show_analytics_page():
    if not is_logged_in():
        st.switch_page("pages/01_Login.py")

    show_sidebar()
    show_header("📈 Application Analytics", "Track your progress and success rates.")

    # Fetch stats from API
    response = api_client.get("/api/applications/stats")
    stats = response.json() if response and response.status_code == 200 else {}

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Applications", stats.get("total_applications", 0))
    with col2:
        st.metric("Success Rate", f"{stats.get('success_rate', 0)}%")
    with col3:
        st.metric("This Week", stats.get("applications_this_week", 0))

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("Platform Distribution")
        df_platform = pd.DataFrame(
            {"Platform": ["LinkedIn", "Indeed", "Google"], "Count": [25, 12, 5]}
        )
        fig = px.pie(df_platform, values="Count", names="Platform", hole=0.4,
                     color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("Monthly Velocity")
        df_trend = pd.DataFrame(
            {"Month": ["Jan", "Feb", "Mar"], "Apps": [10, 45, 82]}
        )
        fig = px.bar(df_trend, x="Month", y="Apps", color="Apps", template="plotly_dark")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    show_analytics_page()
