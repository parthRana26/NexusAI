import streamlit as st
import time
from components import init_page, render_sidebar, render_page_header
from styles import render_metric, render_card, get_theme
from api_client import get_dashboard_stats, get_chat_sessions, NexusAPIError

st.set_page_config(page_title="Dashboard — NexusAI", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

# Init
init_page("Dashboard")
render_sidebar()

# Fetch Stats
with st.spinner("Synchronizing system state..."):
    try:
        # Measure latency
        start_time = time.time()
        stats = get_dashboard_stats()
        latency = int((time.time() - start_time) * 1000)
        
        # Get memory count from stats
        memory_count = stats.get("memory_count", 0) 
    except Exception as e:
        st.error(f"Failed to fetch system stats: {e}")
        stats = {}
        latency = "N/A"
        memory_count = 0

# Header
user = st.session_state.get("user", {})
name = user.get("full_name") or user.get("name", "User")
render_page_header(f"👋 Welcome back, {name}", "Monitor your NexusAI environment and manage your intelligent workflows.")

# Metrics Row
st.subheader("System Performance")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    render_metric("Total Chats", stats.get("total_chats", 0))
with m_col2:
    render_metric("Files Indexed", stats.get("files_uploaded", 0))
with m_col3:
    render_metric("Memory Count", memory_count)
with m_col4:
    render_metric("API Latency", f"{latency}ms")

st.divider()

# Quick Actions Row
st.subheader("Recommended Actions")
col1, col2 = st.columns(2)
with col1:
    render_card("AI Chatbot", "Engage in intelligent conversation and problem solving using our latest models.", "💬")
    if st.button("Start New Conversation →", key="launch_chat", use_container_width=True):
        st.switch_page("pages/chat.py")
with col2:
    render_card("Document RAG", "Query and analyze your uploaded documents with advanced vector search.", "📄")
    if st.button("Manage Documents →", key="launch_docs", use_container_width=True):
        st.switch_page("pages/document_chat.py")

# Activity Feed
st.divider()
st.subheader("Recent Activity")
try:
    sessions = get_chat_sessions()
    if not sessions:
        st.info("No recent activity found. Start a conversation to see it here!")
    else:
        for s in sessions[:5]: # Show last 5
            st.markdown(
                f"""
                <div style="padding:1rem; border-radius:12px; background:{get_theme()['bg_tertiary']}; border-left:4px solid {get_theme()['accent']}; margin-bottom:0.75rem; border:1px solid {get_theme()['border']};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:700; color:{get_theme()['text_primary']};">💬 {s['title']}</span>
                        <span style="font-size:0.7rem; color:{get_theme()['text_muted']};">{s['created_at']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
except Exception:
    st.info("Start chatting to see your activity feed.")