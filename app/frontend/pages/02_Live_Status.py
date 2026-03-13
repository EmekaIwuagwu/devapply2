import streamlit as st
import time
import platform
import os
from app.frontend.components.sidebar import show_sidebar
from app.frontend.utils.auth import is_logged_in
from app.frontend.utils.api_client import api_client
from app.frontend.utils.ui import apply_custom_style

st.set_page_config(page_title="Live Status - DevApply", page_icon="📡", layout="wide")
apply_custom_style()

# ── CSS for log terminal ────────────────────────────────────────────────────
st.markdown("""
<style>
.log-terminal {
    background: #0d1117;
    color: #58d68d;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    padding: 16px;
    border-radius: 10px;
    height: 340px;
    overflow-y: auto;
    border: 1px solid #30363d;
    line-height: 1.6;
}
.log-warn  { color: #f0b429; }
.log-error { color: #e74c3c; }
.log-success { color: #2ecc71; }
.log-info  { color: #58d68d; }
.status-dot-running { display:inline-block; width:10px; height:10px; border-radius:50%; background:#2ecc71; animation: pulse 1.2s infinite; margin-right:6px; }
.status-dot-idle    { display:inline-block; width:10px; height:10px; border-radius:50%; background:#7f8c8d; margin-right:6px; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.metric-card {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 18px 20px;
    border: 1px solid rgba(255,255,255,0.08);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


def _get_system_metrics():
    """Get real system metrics using psutil if available."""
    metrics = {
        "cpu": "N/A", "memory": "N/A",
        "memory_pct": 0, "cpu_pct": 0,
    }
    try:
        import psutil
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.2)
        metrics["cpu"] = f"{cpu:.1f}%"
        metrics["cpu_pct"] = cpu
        metrics["memory"] = f"{mem.used / (1024**3):.1f} GB"
        metrics["memory_pct"] = mem.percent
    except ImportError:
        metrics["cpu"] = "Install psutil"
        metrics["memory"] = "Install psutil"
    return metrics


def _render_log_line(entry: dict) -> str:
    level = entry.get("level", "INFO").upper()
    ts = entry.get("timestamp", "")
    if len(ts) > 19:
        ts = ts[11:19]  # HH:MM:SS
    msg = entry.get("message", "")

    css_class = {
        "WARN": "log-warn", "WARNING": "log-warn",
        "ERROR": "log-error",
        "SUCCESS": "log-success",
    }.get(level, "log-info")

    return f'<span class="{css_class}">[{ts}] [{level}] {msg}</span>'


def show_live_status():
    if not is_logged_in():
        st.switch_page("pages/01_Login.py")

    show_sidebar()

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown("# 📡 Live Agent Status")
    st.markdown("Real-time monitoring of autonomous agent activity.")
    st.markdown("---")

    # ── Fetch real data from backend ─────────────────────────────────────────
    status_data = {"is_running": False, "last_run_status": "idle"}
    status_resp = api_client.get("/api/agents/status")
    if status_resp and status_resp.status_code == 200:
        status_data = status_resp.json()

    log_entries = []
    logs_resp = api_client.get("/api/agents/logs?last_n=100")
    if logs_resp and logs_resp.status_code == 200:
        log_entries = logs_resp.json()

    sys_metrics = _get_system_metrics()
    is_running = status_data.get("is_running", False)
    run_status = status_data.get("last_run_status", "idle")

    # ── Status Banner ────────────────────────────────────────────────────────
    if is_running:
        dot = '<span class="status-dot-running"></span>'
        st.markdown(f'<p style="color:#2ecc71;font-size:16px">{dot}<b>Agents are RUNNING</b> — {run_status}</p>', unsafe_allow_html=True)
    else:
        dot = '<span class="status-dot-idle"></span>'
        label = run_status if run_status != "idle" else "Idle — click 'Start New Run' on the Dashboard to begin"
        st.markdown(f'<p style="color:#7f8c8d;font-size:16px">{dot}<b>Agents are idle</b> — {label}</p>', unsafe_allow_html=True)

    # ── System Metrics ───────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🖥️ CPU Usage", sys_metrics["cpu"])
    with col2:
        st.metric("💾 Memory Usage", sys_metrics["memory"])
    with col3:
        st.metric("📋 Log Entries", len(log_entries))
    with col4:
        agent_state = "🟢 Running" if is_running else "⚪ Idle"
        st.metric("🤖 Agent State", agent_state)

    st.markdown("---")

    # ── Log Terminal ─────────────────────────────────────────────────────────
    col_logs, col_controls = st.columns([3, 1])

    with col_logs:
        st.markdown("### 🖥️ Activity Logs")
        if not log_entries:
            st.markdown("""
            <div class="log-terminal">
                <span class="log-info">[--:--:--] [INFO] Waiting for agents to start...</span><br>
                <span class="log-info">[--:--:--] [INFO] Go to Dashboard → click "Start New Run"</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            lines = [_render_log_line(e) for e in log_entries]
            html_content = "<br>".join(lines)
            # Auto-scroll to bottom
            st.markdown(f"""
            <div class="log-terminal" id="log-terminal">
                {html_content}
            </div>
            <script>
                var el = document.getElementById('log-terminal');
                if(el) el.scrollTop = el.scrollHeight;
            </script>
            """, unsafe_allow_html=True)

    with col_controls:
        st.markdown("### ⚙️ Controls")

        # Auto-refresh toggle
        auto_refresh = st.toggle("Auto Refresh (5s)", value=is_running)
        st.caption("Refreshes the page every 5 seconds when enabled.")

        st.markdown("---")

        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()

        if log_entries:
            if st.button("🗑️ Clear Logs", use_container_width=True):
                clear_resp = api_client.delete("/api/agents/logs")
                st.rerun()

        st.markdown("---")
        # Quick actions
        st.markdown("**Quick Actions**")
        if st.button("📊 Go to Dashboard", use_container_width=True):
            st.switch_page("main.py")
        if st.button("🎯 Edit Strategy", use_container_width=True):
            st.switch_page("pages/03_Strategy.py")

    # ── Mission Progress ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🎯 Mission Progress")

    if log_entries:
        # Calculate real progress from logs
        has_search = any("Step 1" in e.get("message","") or "Search" in e.get("message","") for e in log_entries)
        has_analysis = any("Step 2" in e.get("message","") or "Analys" in e.get("message","") for e in log_entries)
        has_custom = any("Step 3" in e.get("message","") or "Customi" in e.get("message","") for e in log_entries)
        has_applied = any("Step 4" in e.get("message","") or "Submit" in e.get("message","") or "applied" in e.get("message","").lower() for e in log_entries)
        is_done = any("complete" in e.get("message","").lower() or "🎉" in e.get("message","") for e in log_entries)

        steps = [has_search, has_analysis, has_custom, has_applied]
        progress_pct = sum(steps) / 4

        prog_col1, prog_col2, prog_col3, prog_col4 = st.columns(4)
        step_data = [
            ("🔍 Job Search", has_search),
            ("🧠 Analysis", has_analysis),
            ("✍️ Customise", has_custom),
            ("📨 Apply", has_applied),
        ]
        for col, (label, done) in zip([prog_col1, prog_col2, prog_col3, prog_col4], step_data):
            with col:
                icon = "✅" if done else ("⏳" if is_running else "⭕")
                st.markdown(f"**{icon} {label}**")

        st.progress(progress_pct)
        if is_done:
            st.success("🎉 Workflow completed successfully!")
        elif is_running:
            st.info("⏳ Workflow is in progress...")
    else:
        st.progress(0.0)
        st.caption("No active run. Start a new run from the Dashboard.")

    # ── Auto-refresh loop ─────────────────────────────────────────────────────
    if auto_refresh:
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    show_live_status()
