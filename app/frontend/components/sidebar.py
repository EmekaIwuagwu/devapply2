import streamlit as st
from app.frontend.utils.auth import logout


def show_sidebar():
    from app.frontend.utils.auth import is_logged_in
    if not is_logged_in():
        return
        
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2102/2102647.png", width=100)
        st.title("DevApply v1.0")
        st.divider()
        st.page_link("main.py", label="Dashboard", icon="📊")
        st.page_link("pages/02_Live_Status.py", label="Live Status", icon="📡")
        st.page_link("pages/03_Strategy.py", label="Strategy", icon="🎯")
        st.page_link("pages/04_Resume.py", label="📄 Resumes")
        st.page_link("pages/05_Applications.py", label="💼 Applications")
        st.page_link("pages/06_Analytics.py", label="📈 Analytics")
        st.page_link("pages/07_Settings.py", label="⚙️ Settings")
        st.divider()
        if st.button("🚪 Logout"):
            logout()
            st.switch_page("pages/01_Login.py")
