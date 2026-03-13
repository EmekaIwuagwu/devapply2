import streamlit as st
import os


def apply_custom_style():
    css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def show_header(title: str, subtitle: str = None):
    st.markdown(f"""
    <div style="margin-bottom:1.75rem;">
      <div style="
        font-family:'Plus Jakarta Sans',sans-serif;
        font-weight:900; font-size:1.9rem;
        letter-spacing:-0.04em; color:#F8FAFC;
        line-height:1.1; margin-bottom:6px;
      ">{title}</div>
      {f'<div style="color:#475569;font-size:14px;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)
