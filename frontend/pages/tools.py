import streamlit as st
from components import init_page, render_sidebar, render_page_header
from styles import get_theme
from api_client import send_chat

st.set_page_config(page_title="AI Tools — NexusAI", page_icon="🧰", layout="wide", initial_sidebar_state="expanded")

# Init
init_page("AI Tools")
render_sidebar()

# Header
render_page_header("Advanced AI Tools", "Specialized utilities for deep content processing and analysis.")

tabs = st.tabs(["📝 Summarizer", "🔍 Analyzer", "🛠️ Prompt Engineering"])

with tabs[0]:
    st.subheader("Document & Text Summarizer")
    text_to_sum = st.text_area("Enter text or paste document content to summarize:", height=300)
    length = st.select_slider("Summary Length", options=["Short", "Balanced", "Detailed"], value="Balanced")
    
    if st.button("✨ Generate Summary", use_container_width=True):
        if not text_to_sum:
            st.warning("Please enter some text first.")
        else:
            with st.spinner("Summarizing..."):
                try:
                    # We use the general chat endpoint with a specialized prompt
                    system_prompt = (
                        "You are a structured AI tool, not a chatbot. "
                        "Your job is to convert any input into a clear, useful, and structured summary. "
                        "Always interpret short or vague input intelligently (e.g., if 'GenAI skills' is entered, treat it as 'List key GenAI skills'). "
                        "Never ask questions. Never request clarification. Never say 'I need more context'. "
                        "Always produce a complete answer using Title, clear categories, and bullet points. "
                        f"Focus strictly on the provided text. Target length: {length.lower()}."
                    )
                    result = send_chat(text_to_sum, skip_routing=True, system_prompt=system_prompt)
                    st.markdown("### Summary")
                    st.info(result.get("reply", "No response from AI."))
                except Exception as e:
                    st.error(f"Error: {e}")

with tabs[1]:
    st.subheader("Deep Content Analyzer")
    text_to_analyze = st.text_area("Enter content for sentiment, tone, and key entity analysis:", height=300)
    
    if st.button("🔍 Analyze Content", use_container_width=True):
        if not text_to_analyze:
            st.warning("Please enter content to analyze.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    system_prompt = (
                        "You are a deterministic content analyzer tool, not a chatbot. "
                        "Analyze the provided text ONLY for: 1. Sentiment, 2. Tone, 3. Key Entities, 4. Main Topics. "
                        "Never ask questions or for more details. "
                        "Always interpret short inputs into analysis tasks. "
                        "Format the output as a clean, professional report with headings and bullet points."
                    )
                    result = send_chat(text_to_analyze, skip_routing=True, system_prompt=system_prompt)
                    st.markdown("### Analysis Report")
                    st.success(result.get("reply", "No response from AI."))
                except Exception as e:
                    st.error(f"Error: {e}")

with tabs[2]:
    st.subheader("AI Prompt Optimizer")
    raw_prompt = st.text_input("Enter your draft prompt:")
    
    if st.button("🛠️ Optimize Prompt", use_container_width=True):
        if not raw_prompt:
            st.warning("Enter a prompt draft.")
        else:
            with st.spinner("Optimizing..."):
                try:
                    system_prompt = (
                        "You are an AI Prompt Optimizer tool. Your task is to convert any input into a clear, "
                        "detailed, and effective prompt that can be directly used with an AI model. "
                        "You must ONLY output the optimized prompt string. "
                        "Do NOT include explanations, reasoning, headings, or any additional sections. "
                        "No markdown formatting for the title. No 'Optimized Prompt' prefix. "
                        "Always produce a clean, structured, and professional prompt ready for immediate use."
                    )
                    result = send_chat(raw_prompt, skip_routing=True, system_prompt=system_prompt)
                    st.markdown("### 📋 Optimized Prompt")
                    st.code(result.get("reply", "No response from AI."), language="markdown")
                except Exception as e:
                    st.error(f"Error: {e}")
