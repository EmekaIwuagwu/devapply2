import streamlit as st
from app.frontend.utils.auth import login, is_logged_in
from app.frontend.utils.ui import apply_custom_style, show_header

st.set_page_config(page_title="Login - DevApply", page_icon="🔐", layout="centered")
apply_custom_style()


def show_login_page():
    if is_logged_in():
        st.switch_page("main.py")

    # Use columns to center the login container
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        show_header("🔐 DevApply", "Secure Login")
        
        email = st.text_input("Email", placeholder="admin@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        if st.button("Log In"):
            if login(email, password):
                st.success("Welcome back!")
                st.switch_page("main.py")
            else:
                st.error("Invalid credentials.")
        
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.write("Don't have an account?")
        if st.button("Register"):
            st.session_state.show_register = True
            st.rerun()

    if st.session_state.get("show_register"):
        with col2:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.subheader("📝 Register")
            reg_email = st.text_input("Registration Email")
            reg_password = st.text_input("Registration Password", type="password")
            if st.button("Create Account"):
                # This will call /api/auth/register in the future
                st.info("Registration request sent. Implementation pending.")
            
            if st.button("Back to Login"):
                st.session_state.show_register = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    show_login_page()
