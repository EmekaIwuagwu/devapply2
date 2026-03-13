import streamlit as st
import requests
import os

st.set_page_config(
    page_title="DevApply — Sign In",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000").rstrip("/")

# ── Narrow the page + inject rich styling ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800;900&display=swap');

/* Hide sidebar toggle */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] { display: none !important; }

/* Full-page gradient background */
.stApp {
  background:
    radial-gradient(ellipse at 20% 10%,  rgba(124,58,237,0.25) 0%, transparent 50%),
    radial-gradient(ellipse at 85% 90%,  rgba(6,182,212,0.15)  0%, transparent 45%),
    radial-gradient(ellipse at 60% 50%,  rgba(79,70,229,0.08)  0%, transparent 60%),
    #06060f !important;
  min-height: 100vh;
}

/* Narrow centered card container */
.main .block-container {
  max-width: 480px !important;
  padding: 3rem 1.5rem 2rem !important;
  margin: 0 auto !important;
}

/* Card wrapper */
.da-auth-card {
  background: rgba(14, 14, 36, 0.88);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 22px;
  padding: 36px 32px 28px;
  box-shadow:
    0 24px 80px rgba(0,0,0,0.6),
    0 0 0 1px rgba(124,58,237,0.06),
    inset 0 1px 0 rgba(255,255,255,0.06);
}

/* Inputs */
.stTextInput > label {
  font-family: 'Inter', sans-serif !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  color: #475569 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  margin-bottom: 5px !important;
}
.stTextInput > div > div > input {
  background: rgba(255,255,255,0.055) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 10px !important;
  color: #F1F5F9 !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  padding: 11px 14px !important;
  transition: border-color 0.18s, box-shadow 0.18s !important;
}
.stTextInput > div > div > input:focus {
  border-color: #7C3AED !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
  outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #334155 !important; }

/* Primary button */
.stButton > button {
  background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 12px 20px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  letter-spacing: 0.01em !important;
  box-shadow: 0 4px 16px rgba(124,58,237,0.4) !important;
  transition: transform 0.15s, box-shadow 0.15s !important;
  cursor: pointer !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 28px rgba(124,58,237,0.55) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-radius: 7px !important;
  color: #475569 !important;
  font-weight: 700 !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important;
  padding: 9px 0 !important;
  flex: 1 !important;
  justify-content: center !important;
  transition: all 0.15s !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
  color: #fff !important;
  box-shadow: 0 3px 10px rgba(124,58,237,0.45) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; }

/* Alerts */
div[data-testid="stAlert"] { border-radius: 10px !important; margin-top: 10px !important; }
div[data-testid="stSuccess"] > div {
  background: rgba(16,185,129,0.12) !important;
  border: 1px solid rgba(16,185,129,0.28) !important;
  border-radius: 10px !important; color: #6EE7B7 !important;
}
div[data-testid="stError"] > div {
  background: rgba(239,68,68,0.12) !important;
  border: 1px solid rgba(239,68,68,0.28) !important;
  border-radius: 10px !important; color: #FCA5A5 !important;
}
div[data-testid="stInfo"] > div {
  background: rgba(6,182,212,0.1) !important;
  border: 1px solid rgba(6,182,212,0.25) !important;
  border-radius: 10px !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #7C3AED !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbar"] {
  display: none !important; visibility: hidden !important;
}
</style>
""", unsafe_allow_html=True)


def _parse_api_error(resp) -> str:
    """Extract a human-readable error from any API response."""
    try:
        data = resp.json()
        detail = data.get("detail", "")
        if isinstance(detail, list):
            # FastAPI/Pydantic 422 validation error list
            msgs = []
            for err in detail:
                field = err.get("loc", ["?"])[-1] if err.get("loc") else "field"
                msg   = err.get("msg", "invalid")
                msgs.append(f"{field}: {msg}")
            return "; ".join(msgs) if msgs else f"HTTP {resp.status_code}"
        if detail:
            return str(detail)
        return f"HTTP {resp.status_code} — {resp.text[:120]}"
    except Exception:
        return resp.text[:160] if resp.text else f"HTTP {resp.status_code}"


def _do_login(email: str, password: str):
    if not email or not password:
        return False, "Email and password are required."
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            data={"username": email, "password": password},
            timeout=12,
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.logged_in    = True
            st.session_state.user_email   = email
            return True, ""
        return False, _parse_api_error(resp)
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach the server — it may still be warming up. Wait 30 s and try again."
    except Exception as e:
        return False, f"Unexpected error: {e}"


def _do_register(first_name, last_name, email, password, confirm):
    if not all([first_name.strip(), last_name.strip(), email.strip(), password]):
        return False, "All fields are required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if password != confirm:
        return False, "Passwords do not match."
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"email": email.strip(), "password": password,
                  "first_name": first_name.strip(), "last_name": last_name.strip()},
            timeout=12,
        )
        if resp.status_code == 200:
            return True, "Account created! You can now sign in."
        return False, _parse_api_error(resp)
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach the server — it may still be warming up. Wait 30 s and try again."
    except Exception as e:
        return False, f"Unexpected error: {e}"


def show_login_page():
    if st.session_state.get("logged_in"):
        st.switch_page("main.py")

    # ── Brand ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:2rem 0 1.5rem;">
      <div style="font-size:2.8rem; line-height:1; margin-bottom:12px;">⚡</div>
      <div style="
        font-family:'Plus Jakarta Sans',sans-serif;
        font-weight:900; font-size:2.6rem;
        letter-spacing:-0.05em; line-height:1;
        background:linear-gradient(130deg,#F8FAFC 0%,#C4B5FD 45%,#67E8F9 100%);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        background-clip:text;
        margin-bottom:10px;
      ">DevApply</div>
      <div style="color:#475569; font-size:13px; font-family:'Inter',sans-serif;
                  letter-spacing:0.01em;">
        Autonomous AI Job Application Platform
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Card wrapper ───────────────────────────────────────────────────────────
    st.markdown('<div class="da-auth-card">', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["  Sign In  ", "  Create Account  "])

    # ── LOGIN ──────────────────────────────────────────────────────────────────
    with tab_login:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        email    = st.text_input("Email",    placeholder="you@example.com", key="li_email")
        password = st.text_input("Password", placeholder="••••••••",
                                 type="password", key="li_pass")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if st.button("Sign In", type="primary", use_container_width=True, key="btn_li"):
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                with st.spinner("Authenticating…"):
                    ok, msg = _do_login(email, password)
                if ok:
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("""
        <div style='text-align:center; margin-top:16px; color:#334155; font-size:11.5px;
                    font-family:"Inter",sans-serif;'>
          Demo &nbsp;→&nbsp;
          <code style='color:#A78BFA; background:rgba(167,139,250,0.1);
                        padding:2px 6px; border-radius:4px;'>admin@example.com</code>
          &nbsp;/&nbsp;
          <code style='color:#A78BFA; background:rgba(167,139,250,0.1);
                        padding:2px 6px; border-radius:4px;'>password</code>
        </div>
        """, unsafe_allow_html=True)

    # ── REGISTER ───────────────────────────────────────────────────────────────
    with tab_register:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
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
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if st.button("Create Account", type="primary", use_container_width=True, key="btn_reg"):
            with st.spinner("Creating your account…"):
                ok, msg = _do_register(first, last, r_email, r_pass, r_conf)
            if ok:
                st.success(msg)
                st.info("Switch to **Sign In** above to log in.")
            else:
                st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)  # close da-auth-card

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; margin-top:2rem; color:#1E293B;
                font-size:11.5px; font-family:'Inter',sans-serif;">
      DevApply v2.0 &nbsp;·&nbsp; All credentials encrypted at rest
    </div>
    """, unsafe_allow_html=True)


show_login_page()
