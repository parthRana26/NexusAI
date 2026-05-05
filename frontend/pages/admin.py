"""
pages/admin.py — Admin Dashboard Page
"""

import streamlit as st
import time
import pandas as pd
from components import init_page, render_sidebar, render_page_header
from styles import render_metric, get_theme, render_status_badge
from api_client import get_admin_dashboard, get_admin_users, NexusAPIError

st.set_page_config(page_title="Admin Panel — NexusAI", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")

# Role Check (Strict)
user = st.session_state.get("user", {})
if user.get("role") != "admin":
    st.error("⛔ **Access Denied.** You do not have permission to view this page.")
    st.markdown("<div style='text-align:center; margin-top:2rem;'><a href='/' target='_self'>Return to Dashboard</a></div>", unsafe_allow_html=True)
    time.sleep(2)
    st.switch_page("pages/dashboard.py")
    st.stop()

# Init
init_page("Admin")
render_sidebar()

# Header
render_page_header("Admin Command Center", "Platform-wide analytics and user management.")

# ── Data Loading ──────────────────────────────────────────
@st.cache_data(ttl=60) # Cache for 1 minute
def load_admin_data():
    try:
        stats = get_admin_dashboard()
        users = get_admin_users()
        return stats, users
    except Exception as e:
        st.error(f"Failed to sync with admin API: {e}")
        return {}, []

dashboard_data, users_data = load_admin_data()

# ── Analytics Section ─────────────────────────────────────
st.subheader("Platform Health")
cols = st.columns(4)
metrics = [
    ("Total Users", dashboard_data.get("total_users", 0)),
    ("Conversations", dashboard_data.get("total_chats", 0)),
    ("Files Indexed", dashboard_data.get("total_files", 0)),
    ("Active Today", dashboard_data.get("active_today", 0)),
]

for idx, (label, value) in enumerate(metrics):
    with cols[idx % 4]:
        render_metric(label, value)

st.divider()

# ── User Management ───────────────────────────────────────
st.subheader("User Directory")

if users_data:
    df = pd.DataFrame(users_data)
    # Rename columns for display
    df.columns = [col.replace("_", " ").capitalize() for col in df.columns]
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Email": st.column_config.TextColumn("Email Address"),
            "Role": st.column_config.SelectboxColumn("Access Level", options=["user", "admin"]),
        }
    )
    
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("📥 Export User List", use_container_width=True, type="secondary"):
             st.download_button("Download CSV", df.to_csv(index=False), "users.csv", "text/csv")
else:
    st.info("No user records found.")

# ── System Logs ───────────────────────────────────────────
st.divider()
st.subheader("Real-time Event Log")
st.code("""
[SYSTEM] 2026-04-26 22:25:01 - Auth success for user: admin@nexusai.io
[API]    2026-04-26 22:25:05 - GET /api/v1/admin/dashboard - 200 OK
[RAG]    2026-04-26 22:26:10 - Document indexing complete: project_nexus.pdf
""", language="bash")