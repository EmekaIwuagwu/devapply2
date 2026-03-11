import streamlit as st
from app.frontend.utils.api_client import api_client


def is_logged_in():
    return st.session_state.get("logged_in", False)


def login(email, password):
    return api_client.login(email, password)


def logout():
    st.session_state.logged_in = False
    st.session_state.pop("user_email", None)
    st.session_state.pop("access_token", None)
