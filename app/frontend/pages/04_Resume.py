import streamlit as st
from app.frontend.components.sidebar import show_sidebar
from app.frontend.utils.auth import is_logged_in
from app.frontend.utils.api_client import api_client
from app.frontend.utils.ui import apply_custom_style, show_header

st.set_page_config(page_title="Resumes - DevApply", page_icon="📄", layout="wide")
apply_custom_style()


def show_resume_page():
    if not is_logged_in():
        st.switch_page("pages/01_Login.py")

    show_sidebar()
    show_header("📄 Resume Management", "Upload and maintain your master resumes.")

    uploaded_file = st.file_uploader(
        "Upload your base resume (PDF or DOCX)", type=["pdf", "docx"]
    )

    if uploaded_file:
        if st.button("Confirm Upload"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            import requests
            from app.frontend.utils.api_client import BACKEND_URL

            token = st.session_state.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(
                f"{BACKEND_URL}/api/resumes/", headers=headers, files=files
            )
            if res.status_code == 200:
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                st.rerun()
            else:
                st.error("Upload failed.")

    st.divider()

    st.subheader("Your Resumes")
    response = api_client.get("/api/resumes/")
    if response and response.status_code == 200:
        resumes = response.json()
        if not resumes:
            st.write("You haven't uploaded any resumes yet.")
        else:
            for r in resumes:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 **{r['file_name']}** ({r['file_type']})")
                with col2:
                    if st.button("Delete", key=f"del_{r['id']}"):
                        api_client.delete(f"/api/resumes/{r['id']}")
                        st.rerun()
    else:
        st.error("Could not fetch resumes.")


if __name__ == "__main__":
    show_resume_page()
