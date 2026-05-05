"""
app.py — NexusAI Streamlit Entry Point
Handles routing, global theme, and redirects.
"""

import streamlit as st
from components import init_page, render_sidebar
from api_client import get_me, logout

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="NexusAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init Page & Theme ─────────────────────────────────────
init_page("Home")

# ── Auth & Data Loading ──────────────────────────────────
def load_user():
    """Lazy-load current user into session state."""
    if st.session_state.get("access_token") and "user" not in st.session_state:
        try:
            st.session_state["user"] = get_me()
        except Exception:
            logout()
            st.rerun()

# ── Main Entry ────────────────────────────────────────────
def main():
    if st.session_state.get("access_token"):
        load_user()
        render_sidebar()
        
        # Dashboard logic is handled in pages/dashboard.py
        # But we want the root "/" to show the dashboard experience
        st.switch_page("pages/dashboard.py")
                
    else:
        st.switch_page("pages/login.py")

if __name__ == "__main__":
    main()