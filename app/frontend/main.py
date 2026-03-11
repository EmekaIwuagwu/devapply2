import streamlit as st
from app.frontend.components.sidebar import show_sidebar
from app.frontend.utils.auth import is_logged_in
from app.frontend.utils.api_client import api_client
from app.frontend.utils.ui import apply_custom_style, show_header

st.set_page_config(page_title="DevApply Dashboard", page_icon="🚀", layout="wide")
apply_custom_style()


def show_dashboard():
    if not is_logged_in():
        st.switch_page("pages/01_Login.py")

    show_sidebar()
    show_header("🚀 DevApply Dashboard", "Your autonomous job application command center.")

    # Top Row Metrics
    response = api_client.get("/api/applications/stats")
    stats = response.json() if response and response.status_code == 200 else {}

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.metric("Total Apps", stats.get("total_applications", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.metric("Success Rate", f"{stats.get('success_rate', 0)}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.metric("Agents Active", "2")
        st.markdown('</div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.metric("Tokens Saved", "$450")
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom content
    col_left, col_right = st.columns([2, 1])

    # Fetch Active Strategy
    response_strat = api_client.get("/api/strategies/")
    strategies = response_strat.json() if response_strat and response_strat.status_code == 200 else []
    active_strat = next((s for s in strategies if s.get("is_active")), None)

    with col_left:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("🔥 Live Agent Workflow")
        
        # Log placeholder for streaming
        log_container = st.empty()
        
        # Initial logs
        logs = api_client.get("/api/agents/logs")
        log_entries = logs.json() if logs and logs.status_code == 200 else []
        
        if not log_entries:
            log_container.info("Agent is idle. Click 'Start New Run' to begin.")
        else:
            formatted_logs = "\n".join([f"[{e['timestamp'][11:19]}] {e['message']}" for e in log_entries])
            log_container.code(formatted_logs, language="bash")

        col_btn, col_status = st.columns([1, 1])
        with col_btn:
            if st.button("▶️ Start New Run", type="primary", use_container_width=True):
                if active_strat:
                    with st.spinner("Triggering agent workflow..."):
                        start_res = api_client.post(
                            f"/api/agents/start?strategy_id={active_strat['id']}"
                        )
                    if start_res and start_res.status_code == 200:
                        st.toast("🚀 Agent workflow started!", icon="🤖")
                        st.success("✅ Agents are now running. Switch to **Live Status** to monitor progress.")
                        st.rerun()
                    else:
                        err_detail = "Unknown error"
                        if start_res:
                            try:
                                err_detail = start_res.json().get("detail", start_res.text[:200])
                            except Exception:
                                err_detail = start_res.text[:200]
                        st.error(f"❌ Could not start agents: {err_detail}")
                else:
                    st.warning("⚠️ No active strategy found. Please create a strategy first.")
        with col_status:
            if st.button("📡 View Live Status", use_container_width=True):
                st.switch_page("pages/02_Live_Status.py")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("📋 Active Strategy")
        if active_strat:
            st.write(f"**Name:** {active_strat['name']}")
            st.write(f"**Target:** {', '.join(active_strat.get('target_job_titles', []))}")
            st.progress(100 if stats.get("total_applications", 0) > 0 else 0, text="Agent Readiness")
        else:
            st.write("No active strategy found.")
            if st.button("Configure Strategy"):
                st.switch_page("pages/03_Strategy.py")
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    show_dashboard()
