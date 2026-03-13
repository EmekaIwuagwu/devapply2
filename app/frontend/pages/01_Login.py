import streamlit as st
import requests
import os

st.set_page_config(
    page_title="DevApply — Sign In",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
_css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "custom.css")
if os.path.exists(_css_path):
    with open(_css_path) as _f:
        st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] { display: none !important; }
.stApp {
  background:
    radial-gradient(ellipse at 25% 15%, rgba(124,58,237,0.22) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 85%, rgba(6,182,212,0.12)  0%, transparent 50%),
    #060612 !important;
}
.stTextInput > div > div > input {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  color: #F8FAFC !important;
  border-radius: 10px !important;
  font-size: 14px !important;
}
.stTextInput > div > div > input:focus {
  border-color: #7C3AED !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
}
.stTextInput > div > div > input::placeholder { color: #475569 !important; }
.stTextInput > label {
  font-size: 11.5px !important;
  font-weight: 700 !important;
  color: #64748B !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
}
</style>
""", unsafe_allow_html=True)

BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000").rstrip("/")


def _do_login(email: str, password: str):
    if not email or not password:
        return False, "Email and password are required."
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            data={"username": email, "password": password},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.logged_in = True
            st.session_state.user_email = email
            return True, ""
        detail = "Invalid credentials."
        try:
            detail = resp.json().get("detail", detail)
        except Exception:
            pass
        return False, str(detail)
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach the backend server. It may still be starting up — please wait a moment and try again."
    except Exception as e:
        return False, f"Unexpected error: {e}"


def _do_register(first_name, last_name, email, password, confirm):
    if not all([first_name, last_name, email, password]):
        return False, "All fields are required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if password != confirm:
        return False, "Passwords do not match."
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"email": email, "password": password,
                  "first_name": first_name, "last_name": last_name},
            timeout=10,
        )
        if resp.status_code == 200:
            return True, "Account created successfully!"
        detail = "Registration failed."
        try:
            detail = resp.json().get("detail", detail)
        except Exception:
            pass
        return False, str(detail)
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach the backend server. Please try again in a moment."
    except Exception as e:
        return False, f"Unexpected error: {e}"


def show_login_page():
    if st.session_state.get("logged_in"):
        st.switch_page("main.py")

    # Brand header
    st.markdown("""
    <div style="text-align:center; padding: 2.5rem 0 1.75rem;">
      <div style="font-size:2.6rem; margin-bottom:10px; line-height:1;">⚡</div>
      <div style="
        font-family:'Plus Jakarta Sans',sans-serif;
        font-weight:900;
        font-size:2.5rem;
        letter-spacing:-0.05em;
        background:linear-gradient(135deg,#F8FAFC 0%,#A78BFA 55%,#06B6D4 100%);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        background-clip:text;
        line-height:1;
        margin-bottom:10px;
      ">DevApply</div>
      <div style="color:#64748B;font-size:13.5px;font-family:'Inter',sans-serif;letter-spacing:0.01em;">
        Autonomous AI Job Application Platform
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([0.1, 0.8, 0.1])
    with col:
        tab_login, tab_register = st.tabs(["  Sign In  ", "  Create Account  "])

        # LOGIN
        with tab_login:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            email    = st.text_input("Email",    placeholder="you@example.com", key="li_email")
            password = st.text_input("Password", placeholder="••••••••",        key="li_pass",
                                     type="password")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if st.button("Sign In", type="primary", use_container_width=True, key="btn_li"):
                with st.spinner("Authenticating…"):
                    ok, msg = _do_login(email, password)
                if ok:
                    st.success("Welcome back! Loading dashboard…")
                    st.rerun()
                else:
                    st.error(msg)

            st.markdown("""
            <div style='text-align:center;margin-top:18px;color:#475569;font-size:12px;'>
              Demo — <code style='color:#A78BFA'>admin@example.com</code>
              &nbsp;/&nbsp; <code style='color:#A78BFA'>password</code>
            </div>
            """, unsafe_allow_html=True)

        # REGISTER
        with tab_register:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            rc1, rc2 = st.columns(2)
            with rc1:
                first = st.text_input("First Name", placeholder="John",  key="reg_first")
            with rc2:
                last  = st.text_input("Last Name",  placeholder="Doe",   key="reg_last")
            r_email = st.text_input("Email",            placeholder="you@example.com", key="reg_email")
            r_pass  = st.text_input("Password",         placeholder="Min. 8 characters",
                                    type="password", key="reg_pass")
            r_conf  = st.text_input("Confirm Password", placeholder="Repeat password",
                                    type="password", key="reg_conf")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if st.button("Create Account", type="primary", use_container_width=True, key="btn_reg"):
                with st.spinner("Creating your account…"):
                    ok, msg = _do_register(first, last, r_email, r_pass, r_conf)
                if ok:
                    st.success(msg)
                    st.info("Switch to the **Sign In** tab and log in.")
                else:
                    st.error(msg)

    st.markdown("""
    <div style="text-align:center;margin-top:2.5rem;color:#334155;font-size:12px;">
      Powered by DevApply AI Engine &nbsp;·&nbsp; All credentials encrypted at rest
    </div>
    """, unsafe_allow_html=True)


show_login_page()
