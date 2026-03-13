import streamlit as st


NAV_ITEMS = [
    ("main.py",                  "📊", "Dashboard"),
    ("pages/02_Live_Status.py",  "📡", "Live Status"),
    ("pages/03_Strategy.py",     "🎯", "Strategy"),
    ("pages/04_Resume.py",       "📄", "Resumes"),
    ("pages/05_Applications.py", "💼", "Applications"),
    ("pages/06_Analytics.py",    "📈", "Analytics"),
    ("pages/07_Settings.py",     "⚙️",  "Settings"),
]


def show_sidebar():
    from app.frontend.utils.auth import is_logged_in, logout

    if not is_logged_in():
        return

    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding: 0 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 16px;">
          <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:1.4rem;">⚡</span>
            <span style="
              font-family:'Plus Jakarta Sans',sans-serif;
              font-weight:900;
              font-size:1.25rem;
              letter-spacing:-0.04em;
              background:linear-gradient(135deg,#F8FAFC 0%,#A78BFA 60%,#06B6D4 100%);
              -webkit-background-clip:text;
              -webkit-text-fill-color:transparent;
              background-clip:text;
            ">DevApply</span>
          </div>
          <div style="color:#334155; font-size:11px; margin-top:4px; padding-left:2px; letter-spacing:0.03em;">
            AI Job Application Engine
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Nav label
        st.markdown("""
        <div style="padding:0 16px 8px; color:#334155; font-size:10.5px;
                    font-weight:700; letter-spacing:0.08em; text-transform:uppercase;">
          Navigation
        </div>
        """, unsafe_allow_html=True)

        # Pages
        for path, icon, label in NAV_ITEMS:
            st.page_link(path, label=f"{icon}  {label}")

        st.markdown("<div style='height:1px; background:rgba(255,255,255,0.07); margin:16px 0;'></div>",
                    unsafe_allow_html=True)

        # User info
        user_email = st.session_state.get("user_email", "")
        if user_email:
            st.markdown(f"""
            <div style="padding:10px 14px; background:rgba(255,255,255,0.04);
                        border-radius:10px; margin:0 0 12px;">
              <div style="font-size:11px; color:#334155; font-weight:600;
                          text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;">
                Signed in as
              </div>
              <div style="font-size:12.5px; color:#A78BFA; font-weight:600;
                          overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                {user_email}
              </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("Sign Out", key="sidebar_logout", use_container_width=True):
            logout()
            st.switch_page("pages/01_Login.py")

        # Version
        st.markdown("""
        <div style="position:fixed; bottom:20px; left:0; right:0; text-align:center;
                    color:#1E293B; font-size:10.5px; letter-spacing:0.04em;">
          DevApply v2.0
        </div>
        """, unsafe_allow_html=True)
