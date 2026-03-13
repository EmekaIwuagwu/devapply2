import streamlit as st
from app.frontend.components.sidebar import show_sidebar
from app.frontend.utils.auth import is_logged_in
from app.frontend.utils.api_client import api_client
from app.frontend.utils.ui import apply_custom_style

st.set_page_config(
    page_title="DevApply — Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_style()


def show_dashboard():
    if not is_logged_in():
        st.switch_page("pages/01_Login.py")

    show_sidebar()

    # ── Page Header ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom:1.75rem;">
      <div style="
        font-family:'Plus Jakarta Sans',sans-serif;
        font-weight:900;
        font-size:1.9rem;
        letter-spacing:-0.04em;
        color:#F8FAFC;
        line-height:1.1;
        margin-bottom:6px;
      ">Command Center</div>
      <div style="color:#475569; font-size:14px;">
        Your autonomous job application engine — live stats, logs &amp; controls.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch Stats ───────────────────────────────────────────────────────────
    stats = {}
    resp = api_client.get("/api/applications/stats")
    if resp and resp.status_code == 200:
        stats = resp.json()

    # ── KPI Row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Applications", stats.get("total_applications", 0))
    with c2:
        sr = stats.get("success_rate", 0)
        st.metric("Interview Rate", f"{sr:.1f}%")
    with c3:
        st.metric("This Week", stats.get("applications_this_week", 0))
    with c4:
        # Fetch agent status
        agent_status = {}
        sr2 = api_client.get("/api/agents/status")
        if sr2 and sr2.status_code == 200:
            agent_status = sr2.json()
        running = agent_status.get("is_running", False)
        st.metric("Agent State", "🟢 Running" if running else "⚪ Idle")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Main Content Row ──────────────────────────────────────────────────────
    left, right = st.columns([2, 1], gap="large")

    # Fetch logs and strategies in parallel (sequential for simplicity)
    logs_resp = api_client.get("/api/agents/logs?last_n=50")
    log_entries = logs_resp.json() if logs_resp and logs_resp.status_code == 200 else []

    strat_resp = api_client.get("/api/strategies/")
    strategies = strat_resp.json() if strat_resp and strat_resp.status_code == 200 else []
    active_strat = next((s for s in strategies if s.get("is_active")), None)

    # ── Activity Panel ────────────────────────────────────────────────────────
    with left:
        st.markdown("""
        <div style="
          font-family:'Plus Jakarta Sans',sans-serif;
          font-weight:700; font-size:1rem; color:#F8FAFC;
          margin-bottom:14px; display:flex; align-items:center; gap:8px;
        ">
          <span>🖥️</span> Live Agent Activity
        </div>
        """, unsafe_allow_html=True)

        if not log_entries:
            st.markdown("""
            <div class="log-terminal">
              <span class="log-info">[--:--:--] [INFO] Agent engine is idle.</span><br>
              <span class="log-info">[--:--:--] [INFO] Configure a strategy and click Start New Run.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            lines = []
            for e in log_entries:
                ts  = e.get("timestamp", "")
                ts  = ts[11:19] if len(ts) >= 19 else "--:--:--"
                lvl = e.get("level", "INFO").upper()
                msg = e.get("message", "")
                css = {"WARN": "log-warn", "WARNING": "log-warn",
                       "ERROR": "log-error", "SUCCESS": "log-success"}.get(lvl, "log-info")
                lines.append(f'<span class="{css}">[{ts}] [{lvl}] {msg}</span>')
            body = "<br>".join(lines)
            st.markdown(f"""
            <div class="log-terminal" id="da-log">
              {body}
            </div>
            <script>
              var el=document.getElementById('da-log');
              if(el) el.scrollTop=el.scrollHeight;
            </script>
            """, unsafe_allow_html=True)

        # Controls
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("▶ Start New Run", type="primary", use_container_width=True, key="dashboard_start"):
                if active_strat:
                    with st.spinner("Triggering agent workflow…"):
                        r = api_client.post(f"/api/agents/start?strategy_id={active_strat['id']}")
                    if r and r.status_code == 200:
                        st.toast("Agent workflow started!", icon="🤖")
                        st.rerun()
                    else:
                        detail = "Unknown error"
                        if r:
                            try:
                                detail = r.json().get("detail", r.text[:200])
                            except Exception:
                                detail = r.text[:200] if r.text else "No response"
                        st.error(f"Could not start agents: {detail}")
                else:
                    st.warning("No active strategy found. Create one in the Strategy page first.")
        with btn_col2:
            if st.button("📡 Live Status", use_container_width=True, key="dashboard_live"):
                st.switch_page("pages/02_Live_Status.py")
        with btn_col3:
            if st.button("🔄 Refresh", use_container_width=True, key="dashboard_refresh"):
                st.rerun()

    # ── Right Panel ───────────────────────────────────────────────────────────
    with right:
        # Active Strategy card
        st.markdown("""
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                    font-size:1rem;color:#F8FAFC;margin-bottom:14px;
                    display:flex;align-items:center;gap:8px;">
          <span>🎯</span> Active Strategy
        </div>
        """, unsafe_allow_html=True)

        if active_strat:
            titles = active_strat.get("target_job_titles") or []
            locs   = active_strat.get("location_preference") or []
            types  = active_strat.get("job_types") or []
            total_apps = stats.get("total_applications", 0)

            st.markdown(f"""
            <div class="da-card">
              <div style="font-weight:700;font-size:1rem;color:#F8FAFC;margin-bottom:12px;">
                {active_strat.get('name','—')}
              </div>
              <div style="font-size:12.5px;color:#64748B;font-weight:700;
                          text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">
                Target Roles
              </div>
              <div style="margin-bottom:12px;">
                {''.join(f'<span class="da-badge da-badge-purple" style="margin-right:4px;margin-bottom:4px;">{t}</span>' for t in titles[:4]) or '<span style="color:#475569;font-size:13px;">Not set</span>'}
              </div>
              {'<div style="font-size:12.5px;color:#64748B;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Location</div><div style="margin-bottom:12px;">' + ''.join(f'<span class="da-badge da-badge-blue" style="margin-right:4px;">{l}</span>' for l in locs) + '</div>' if locs else ''}
              {'<div style="font-size:12.5px;color:#64748B;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Type</div><div style="margin-bottom:12px;">' + ''.join(f'<span class="da-badge da-badge-green" style="margin-right:4px;">{tp}</span>' for tp in types) + '</div>' if types else ''}
            </div>
            """, unsafe_allow_html=True)

            readiness = min(100, total_apps * 2) if total_apps else 0
            st.progress(readiness / 100, text=f"Readiness {readiness}%")
        else:
            st.markdown("""
            <div class="da-card" style="text-align:center;padding:32px 20px;">
              <div style="font-size:2rem;margin-bottom:12px;">🎯</div>
              <div style="color:#94A3B8;font-size:14px;margin-bottom:16px;">
                No active strategy configured
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Configure Strategy →", type="primary", use_container_width=True):
                st.switch_page("pages/03_Strategy.py")

        # Quick links
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;
                    font-size:1rem;color:#F8FAFC;margin-bottom:10px;
                    display:flex;align-items:center;gap:8px;">
          <span>⚡</span> Quick Actions
        </div>
        """, unsafe_allow_html=True)

        qa1, qa2 = st.columns(2)
        with qa1:
            if st.button("📄 Resumes",      use_container_width=True, key="qa_resumes"):
                st.switch_page("pages/04_Resume.py")
        with qa2:
            if st.button("📈 Analytics",    use_container_width=True, key="qa_analytics"):
                st.switch_page("pages/06_Analytics.py")
        if st.button("💼 View Applications", use_container_width=True, key="qa_apps"):
            st.switch_page("pages/05_Applications.py")


show_dashboard()
