"""
pages/profile.py — User Profile Page
"""

import streamlit as st
from components import init_page, render_sidebar, render_page_header
from styles import get_theme, render_card
from api_client import get_me, NexusAPIError, update_user_preferences, logout
import json

st.set_page_config(page_title="Profile — NexusAI", page_icon="👤", layout="wide", initial_sidebar_state="expanded")

# Init
init_page("Profile")
render_sidebar()

# Load User Data
user = st.session_state.get("user")
if not user:
    with st.spinner("Synchronizing..."):
        try:
            user = get_me()
            st.session_state["user"] = user
        except Exception:
            st.error("Could not load profile. Please sign in again.")
            st.stop()

# Header
render_page_header("Account Profile", "Manage your personal information and preferences.")

# Layout
theme = get_theme()
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    # Avatar Section
    name = user.get("name") or user.get("full_name") or "User"
    initial = name[0].upper() if name else "👤"
    st.markdown(
        f"""
        <div style="background:{theme['bg_secondary']}; border:1px solid {theme['border']}; border-radius:24px; padding:3rem 2rem; text-align:center;">
            <div style="width:120px; height:120px; border-radius:50%; background:linear-gradient(135deg, {theme['accent']}, {theme['accent_strong']}); margin:0 auto 1.5rem auto; display:flex; align-items:center; justify-content:center; font-size:4rem; color:white; box-shadow:0 10px 25px {theme['accent']}44;">
                {initial}
            </div>
            <h2 style="margin:0; font-size:1.5rem; font-weight:800;">{name}</h2>
            <p style="margin:0.5rem 0 0 0; color:{theme['text_muted']}; font-size:0.9rem;">{user.get('email')}</p>
            <div style="margin-top:1.5rem;">
                <span style="background:{theme['success']}22; color:{theme['success']}; padding:4px 12px; border-radius:99px; font-size:0.75rem; font-weight:700; border:1px solid {theme['success']}44;">
                    Verified Account
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.subheader("General Information")
    
    # Information Grid
    details = [
        ("Full Name", user.get("name") or user.get("full_name", "N/A"), "👤"),
        ("Email Address", user.get("email", "N/A"), "📧"),
        ("Platform Role", user.get("role", "user").capitalize(), "🛡️"),
        ("Member Since", user.get("created_at", "N/A")[:10] if user.get("created_at") else "N/A", "📅"),
    ]
    
    for label, value, icon in details:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; justify-content:space-between; padding:1.25rem; border-bottom:1px solid {theme['border']};">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:1.2rem;">{icon}</span>
                    <span style="font-weight:600; color:{theme['text_secondary']};">{label}</span>
                </div>
                <span style="font-weight:700; color:{theme['text_primary']};">{value}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.subheader("API Settings")
    
    # Load current key from preferences
    prefs = user.get("preferences", {})
    if isinstance(prefs, str):
        try:
            prefs = json.loads(prefs)
        except:
            prefs = {}
    
    current_key = prefs.get("groq_api_key", "")
    
    with st.form("api_key_form"):
        new_key = st.text_input(
            "Groq API Key", 
            value=current_key, 
            type="password",
            help="If provided, NexusAI will use your personal key instead of the system default."
        )
        if st.form_submit_button("Save API Settings", use_container_width=True, type="primary"):
            prefs["groq_api_key"] = new_key
            try:
                update_user_preferences(prefs)
                st.success("API settings updated!")
                st.session_state["user"]["preferences"] = prefs
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update settings: {e}")

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        logout()
        st.rerun()