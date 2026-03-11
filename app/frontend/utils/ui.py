import streamlit as st
import os

def apply_custom_style():
    css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_header(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.write(f"#### {subtitle}")
    st.divider()
