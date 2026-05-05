"""
pages/chat.py — ChatGPT-style Chat Interface
"""

import streamlit as st
from components import init_page, render_sidebar, render_page_header
from styles import render_chat_message, get_theme
from api_client import send_chat, NexusAPIError

st.set_page_config(page_title="Chat — NexusAI", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

# Init
init_page("Chat")
render_sidebar()

# Header
render_page_header("Chat with AI", "Powered by NexusAI Omni-Routing Engine")

# ── Chat State & Sync ──────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Load history if session_id is newly selected or chat_history is empty
session_id = st.session_state.get("current_session_id")
if session_id and not st.session_state["chat_history"]:
    from api_client import get_session_messages
    try:
        with st.spinner("Loading history..."):
            history = get_session_messages(session_id)
            st.session_state["chat_history"] = [
                {"role": "user" if m["role"] == "user" else "ai", "content": m["content"]}
                for m in history
            ]
    except Exception as e:
        st.error(f"Failed to load history: {e}")

# ── Chat Display ───────────────────────────────────────
chat_container = st.container(height=600)

with chat_container:
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"] if msg["role"] == "user" else "assistant"):
            st.write(msg["content"])

# ── Chat Input ─────────────────────────────────────────
if prompt := st.chat_input("Send a message to NexusAI..."):
    # Add user message
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    
    # Display user message immediately
    with chat_container:
        with st.chat_message("user"):
            st.write(prompt)

    # Process AI response
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                try:
                    session_id = st.session_state.get("current_session_id")
                    resp = send_chat(prompt, session_id=session_id)
                    
                    if "session_id" in resp:
                        st.session_state["current_session_id"] = resp["session_id"]
                    
                    ai_reply = resp.get("reply", "No response received.")
                    st.write(ai_reply)
                    
                    st.session_state["chat_history"].append({"role": "ai", "content": ai_reply})
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.rerun()

# ── Footer Actions ─────────────────────────────────────
if st.session_state["chat_history"]:
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state["chat_history"] = []
        st.session_state.pop("current_session_id", None)
        st.rerun()