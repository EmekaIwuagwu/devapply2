import streamlit as st
from app.frontend.components.sidebar import show_sidebar
from app.frontend.utils.auth import is_logged_in
from app.frontend.utils.api_client import api_client
from app.frontend.utils.ui import apply_custom_style, show_header

st.set_page_config(page_title="Applications - DevApply", page_icon="💼", layout="wide")
apply_custom_style()

st.markdown("""
<style>
.app-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.app-card:hover { border-color: rgba(139,92,246,0.5); }
.status-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.badge-applied   { background: rgba(59,130,246,0.2);  color: #60a5fa; }
.badge-interview { background: rgba(34,197,94,0.2);   color: #4ade80; }
.badge-rejected  { background: rgba(239,68,68,0.2);   color: #f87171; }
.badge-pending   { background: rgba(234,179,8,0.2);   color: #facc15; }
.score-bar-wrap { background: rgba(255,255,255,0.08); border-radius: 6px; height: 6px; margin-top: 4px; }
.score-bar { height: 6px; border-radius: 6px; background: linear-gradient(90deg, #8b5cf6, #3b82f6); }
</style>
""", unsafe_allow_html=True)

STATUS_ICONS = {
    "Applied": "📨",
    "Interview": "🎯",
    "Rejected": "❌",
    "Pending": "⏳",
    "Offer": "🎉",
}

PLATFORM_ICONS = {
    "LinkedIn": "🔵",
    "RemoteOK": "🌐",
    "Adzuna": "🔍",
    "Indeed": "🟡",
    "Google Jobs": "🔴",
}


def _badge_class(status: str) -> str:
    return {
        "Applied": "badge-applied",
        "Interview": "badge-interview",
        "Rejected": "badge-rejected",
    }.get(status, "badge-pending")


def show_applications_page():
    if not is_logged_in():
        st.switch_page("pages/01_Login.py")

    show_sidebar()
    show_header("💼 Application History", "Every autonomous submission, tracked in real-time.")

    # ── Top stats ─────────────────────────────────────────────────────────────
    stats_resp = api_client.get("/api/applications/stats")
    stats = stats_resp.json() if stats_resp and stats_resp.status_code == 200 else {}

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📨 Total Applied", stats.get("total_applications", 0))
    with c2:
        st.metric("📅 This Week", stats.get("applications_this_week", 0))
    with c3:
        rate = stats.get("success_rate", 0)
        st.metric("🎯 Interview Rate", f"{rate:.1f}%")
    with c4:
        st.metric("🏆 Interviews", "—")

    st.markdown("---")

    # ── Fetch applications ────────────────────────────────────────────────────
    response = api_client.get("/api/applications/")
    if not response or response.status_code != 200:
        st.error("❌ Failed to fetch applications from the backend.")
        return

    apps = response.json()

    if not apps:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color: #7f8c8d;">
            <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
            <h3>No applications yet</h3>
            <p>Go to the Dashboard and click <strong>▶️ Start New Run</strong> to let the agents find and apply to jobs for you.</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Go to Dashboard", use_container_width=True, type="primary"):
                st.switch_page("main.py")
        return

    # ── Filter bar ────────────────────────────────────────────────────────────
    col_filter, col_sort = st.columns([2, 1])
    with col_filter:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Applied", "Interview", "Pending", "Rejected", "Offer"],
            label_visibility="collapsed",
        )
    with col_sort:
        sort_by = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Highest Match Score"],
            label_visibility="collapsed",
        )

    # Apply filters
    filtered = apps
    if status_filter != "All":
        filtered = [a for a in apps if a.get("status") == status_filter]

    if sort_by == "Oldest First":
        filtered = sorted(filtered, key=lambda a: a.get("applied_date", ""))
    elif sort_by == "Highest Match Score":
        filtered = sorted(filtered, key=lambda a: a.get("match_score") or 0, reverse=True)
    else:
        filtered = sorted(filtered, key=lambda a: a.get("applied_date", ""), reverse=True)

    st.markdown(f"**{len(filtered)} application(s) found**")
    st.markdown("")

    # ── Application cards ─────────────────────────────────────────────────────
    for app in filtered:
        status = app.get("status", "Pending")
        platform = app.get("platform", "Unknown")
        score = app.get("match_score") or 0
        title = app.get("job_title", "Unknown Role")
        company = app.get("company_name", "Unknown Company")
        date_raw = app.get("applied_date", "")
        date_str = date_raw[0:10] if len(date_raw) >= 10 else "—"
        url = app.get("job_url", "")

        status_icon = STATUS_ICONS.get(status, "📄")
        platform_icon = PLATFORM_ICONS.get(platform, "🌐")
        badge_cls = _badge_class(status)

        score_width = f"{score}%"

        url_html = f'<a href="{url}" target="_blank" style="color:#8b5cf6; font-size:12px; text-decoration:none;">🔗 View Job</a>' if url else ""

        st.markdown(f"""
        <div class="app-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div style="font-size:17px; font-weight:700; margin-bottom:4px;">{title}</div>
                    <div style="color:#9ca3af; font-size:14px;">{platform_icon} {company} &nbsp;·&nbsp; {platform} &nbsp;·&nbsp; {date_str}</div>
                </div>
                <div style="text-align:right;">
                    <span class="status-badge {badge_cls}">{status_icon} {status}</span>
                    {f'<div style="margin-top:6px;">{url_html}</div>' if url else ""}
                </div>
            </div>
            {f'''<div style="margin-top:12px;">
                <div style="font-size:12px; color:#9ca3af; margin-bottom:3px;">Match Score: <b style="color:#c4b5fd;">{score}/100</b></div>
                <div class="score-bar-wrap"><div class="score-bar" style="width:{score_width};"></div></div>
            </div>''' if score else ""}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    if st.button("🔄 Refresh", use_container_width=False):
        st.rerun()


if __name__ == "__main__":
    show_applications_page()
