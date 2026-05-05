import streamlit as st
from components import init_page, render_sidebar, render_page_header
from styles import get_theme
from api_client import upload_file, get_files, delete_file, query_docs, NexusAPIError

st.set_page_config(page_title="Document Chat — NexusAI", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

# Init
init_page("Document Chat")
render_sidebar()

# Header
render_page_header("Document Intelligence", "Upload, manage, and chat with your documents using Qdrant-powered RAG.")

# State Management for Chat
if "doc_chat_history" not in st.session_state:
    st.session_state["doc_chat_history"] = []

# Layout
col_files, col_chat = st.columns([1, 1.5], gap="large")

with col_files:
    st.subheader("📁 File Manager")
    
    # Upload Section
    with st.expander("📤 Upload New Document", expanded=False):
        uploaded_file = st.file_uploader(
            "Select File",
            type=["pdf", "docx", "txt", "csv", "jpg", "png"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            category = st.selectbox("Category", ["general", "research", "financial", "legal"], key="doc_cat")
            if st.button("🚀 Index Document", use_container_width=True):
                with st.spinner("Processing..."):
                    try:
                        upload_file(
                            file_bytes=uploaded_file.getvalue(),
                            filename=uploaded_file.name,
                            content_type=uploaded_file.type,
                            category=category
                        )
                        st.success("Indexed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    st.divider()

    # File List
    try:
        files = get_files()
        if not files:
            st.info("No documents indexed yet.")
        else:
            for f in files:
                with st.container():
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"**{f['filename']}**  \n`{f['category']}` • {f['file_size'] // 1024} KB")
                    if c2.button("🗑️", key=f"del_{f['id']}", help="Delete file"):
                        try:
                            delete_file(f["id"])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")
                st.divider()
    except Exception as e:
        st.error("Could not load files.")

with col_chat:
    st.subheader("💬 Document Chat")
    
    # Chat Display
    chat_container = st.container(height=500)
    with chat_container:
        if not st.session_state["doc_chat_history"]:
            st.info("Ask a question about your indexed documents to start.")
        else:
            for msg in st.session_state["doc_chat_history"]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if "context" in msg and msg["context"]:
                        with st.expander("🔍 Sources"):
                            st.caption(msg["context"])

    # Chat Input
    if prompt := st.chat_input("Ask something about your documents..."):
        # Add user message
        st.session_state["doc_chat_history"].append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Retrieving and analyzing..."):
                try:
                    result = query_docs(prompt)
                    answer = result.get("answer", "I couldn't find an answer in your documents.")
                    context = result.get("context", "")
                    
                    st.write(answer)
                    if context:
                        with st.expander("🔍 Sources"):
                            st.caption(context)
                            
                    st.session_state["doc_chat_history"].append({
                        "role": "assistant", 
                        "content": answer,
                        "context": context
                    })
                except Exception as e:
                    st.error(f"Query failed: {e}")

if st.button("🧹 Clear Chat History", type="secondary"):
    st.session_state["doc_chat_history"] = []
    st.rerun()