import streamlit as st
from app.frontend.components.sidebar import show_sidebar
from app.frontend.utils.auth import is_logged_in
from app.frontend.utils.api_client import api_client
from app.frontend.utils.ui import apply_custom_style, show_header

st.set_page_config(page_title="Settings - DevApply", page_icon="⚙️", layout="wide")
apply_custom_style()


def show_settings_page():
    if not is_logged_in():
        st.switch_page("pages/01_Login.py")

    show_sidebar()
    show_header("⚙️ User Settings", "Manage your profile and agent preferences.")

    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    
    # Fetch user profile
    user_profile = {}
    resp = api_client.get("/api/users/me")
    if resp and resp.status_code == 200:
        user_profile = resp.json()

    with st.expander("👤 Personal Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", value=user_profile.get("first_name") or "Admin")
            last_name = st.text_input("Last Name", value=user_profile.get("last_name") or "User")
            email = st.text_input("Email", value=user_profile.get("email") or "admin@example.com", disabled=True)
        with col2:
            linkedin_url = st.text_input("LinkedIn URL", value=user_profile.get("linkedin_url") or "", placeholder="https://linkedin.com/in/...")
            github_url = st.text_input("GitHub URL", value=user_profile.get("github_url") or "", placeholder="https://github.com/...")
            portfolio_url = st.text_input("Portfolio URL", value=user_profile.get("portfolio_url") or "", placeholder="https://yourwebsite.com")
            
        profile_bio = st.text_area("Cover Letter Template / Bio", value=user_profile.get("profile_bio") or "", height=150)

        if st.button("Update Profile"):
            update_data = {
                "first_name": first_name,
                "last_name": last_name,
                "linkedin_url": linkedin_url,
                "github_url": github_url,
                "portfolio_url": portfolio_url,
                "profile_bio": profile_bio
            }
            user_id = user_profile.get("id")
            if user_id:
                update_resp = api_client.put(f"/api/users/{user_id}", data=update_data)
                if update_resp and update_resp.status_code == 200:
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile.")
            else:
                st.error("User context missing.")

    with st.expander("🔑 LinkedIn Easy Apply Credentials"):
        st.markdown(
            "Store your LinkedIn credentials so the agent can log in and submit Easy Apply "
            "applications on your behalf. Your password is **encrypted at rest** and never "
            "exposed through the API."
        )

        # Fetch current status
        cred_resp = api_client.get("/api/users/me/linkedin-credentials/status")
        cred_status = cred_resp.json() if cred_resp and cred_resp.status_code == 200 else {}
        stored_email = cred_status.get("linkedin_email") or ""
        has_password = cred_status.get("has_password", False)

        if stored_email or has_password:
            st.info(
                f"✅ Credentials saved — Email: **{stored_email or '(not set)'}** | "
                f"Password: {'✔ stored' if has_password else '✘ not set'}"
            )
        else:
            st.warning("No LinkedIn credentials saved yet.")

        li_email = st.text_input(
            "LinkedIn Email", value=stored_email, placeholder="you@example.com", key="li_email"
        )
        li_password = st.text_input(
            "LinkedIn Password", type="password", placeholder="Enter password", key="li_password"
        )

        col_save, col_clear = st.columns([1, 1])
        with col_save:
            if st.button("💾 Save Credentials"):
                if not li_email or not li_password:
                    st.error("Both email and password are required.")
                else:
                    save_resp = api_client.post(
                        "/api/users/me/linkedin-credentials",
                        data={"email": li_email, "password": li_password},
                    )
                    if save_resp and save_resp.status_code == 200:
                        st.success("LinkedIn credentials saved and encrypted!")
                        st.rerun()
                    else:
                        err = save_resp.json() if save_resp else {}
                        st.error(f"Failed to save: {err.get('detail', 'Unknown error')}")
        with col_clear:
            if st.button("🗑️ Clear Credentials"):
                del_resp = api_client.delete("/api/users/me/linkedin-credentials")
                if del_resp and del_resp.status_code == 200:
                    st.success("LinkedIn credentials removed.")
                    st.rerun()
                else:
                    st.error("Failed to clear credentials.")

    with st.expander("🤖 Agent Settings"):
        st.number_input("Max applications per run", value=10, min_value=1, max_value=50)
        st.checkbox("Enable Stealth Mode", value=True)
        st.checkbox("Auto-apply if match > 90%", value=False)
        if st.button("Save Agent Config"):
            st.success("Agent configuration saved!")

    st.divider()
    if st.button("🗑️ Delete Account", type="primary"):
        st.warning("This action is irreversible.")
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    show_settings_page()
