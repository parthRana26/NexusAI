"""
styles.py — Premium SaaS Theme System for NexusAI
Manages Dark/Light themes with high-contrast, polished aesthetics.
"""

import streamlit as st


# ── Color Palettes ─────────────────────────────────────

DARK = {
    "bg": "#0a0a0f",
    "bg_secondary": "#12121a",
    "bg_tertiary": "#1a1a25",
    "surface": "#1e1e2e",
    "surface_hover": "#252538",
    "border": "#2a2a3c",
    "border_focus": "#6366f1",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "accent": "#818cf8",
    "accent_hover": "#a5b4fc",
    "accent_strong": "#6366f1",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#3b82f6",
    "shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3)",
    "shadow_card": "0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -4px rgba(0, 0, 0, 0.4)",
    "gradient_sidebar": "linear-gradient(180deg, #12121a 0%, #0a0a0f 100%)",
}

LIGHT = {
    "bg": "#fafafa",
    "bg_secondary": "#ffffff",
    "bg_tertiary": "#f8fafc",
    "surface": "#ffffff",
    "surface_hover": "#f1f5f9",
    "border": "#e2e8f0",
    "border_focus": "#4f46e5",
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_muted": "#94a3b8",
    "accent": "#4f46e5",
    "accent_hover": "#6366f1",
    "accent_strong": "#4338ca",
    "success": "#16a34a",
    "warning": "#d97706",
    "danger": "#dc2626",
    "info": "#2563eb",
    "shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.04)",
    "shadow_card": "0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04)",
    "gradient_sidebar": "linear-gradient(180deg, #ffffff 0%, #fafafa 100%)",
}


def get_theme() -> dict:
    """Return the active theme palette from session_state."""
    return DARK if st.session_state.get("theme") == "dark" else LIGHT


def toggle_theme():
    """Toggle between dark and light themes."""
    current = st.session_state.get("theme", "light")
    st.session_state["theme"] = "dark" if current == "light" else "light"


def apply_theme():
    """Apply the current theme CSS globally."""
    theme = get_theme()

    css = f"""
    <style>
    /* ── Global Reset ── */
    .stApp {{
        background-color: {theme['bg']};
        color: {theme['text_primary']};
    }}
    
    /* ── Main Content Area ── */
    .main .block-container {{
        padding-top: 4rem;
        padding-bottom: 6rem;
        max-width: 1100px;
    }}
    
    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: {theme['gradient_sidebar']} !important;
        border-right: 1px solid {theme['border']};
    }}
    
    /* ── Typography ── */
    h1, h2, h3, h4, h5, h6 {{
        color: {theme['text_primary']} !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em;
    }}
    
    /* ── Buttons ── */
    .stButton>button {{
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px {theme['accent']}44;
    }}

    /* ── Chat Bubbles ── */
    .chat-bubble {{
        padding: 1.25rem 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        max-width: 85%;
        line-height: 1.6;
        font-size: 1.05rem;
        animation: fadeIn 0.4s ease-out;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .user-bubble {{
        background-color: {theme['accent']};
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }}

    .ai-bubble {{
        background-color: {theme['bg_secondary']};
        color: {theme['text_primary']};
        margin-right: auto;
        border-bottom-left-radius: 4px;
        border: 1px solid {theme['border']};
    }}

    /* ── Custom Cards ── */
    .nexus-card {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        box-shadow: {theme['shadow_card']};
    }}
    
    .nexus-metric {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: {theme['shadow']};
    }}
    .nexus-metric .value {{
        font-size: 2.5rem;
        font-weight: 800;
        color: {theme['accent']};
    }}

    /* ── Hide Streamlit Branding & Default Nav ── */
    /* ── Hide Streamlit Branding ── */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Force Sidebar Toggle Visibility */
    [data-testid="stSidebarCollapseButton"] {{
        visibility: visible !important;
        display: flex !important;
        background-color: {theme['bg_secondary']} !important;
        border: 1px solid {theme['border']} !important;
        border-radius: 8px !important;
        color: {theme['text_primary']} !important;
        z-index: 999999 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_card(title: str, content: str, icon: str = ""):
    """Render a polished card component."""
    icon_html = f'<span style="font-size:1.75rem;margin-right:0.75rem;">{icon}</span>' if icon else ""
    st.markdown(
        f"""
        <div class="nexus-card">
            <h3 style="margin:0 0 0.75rem 0;">{icon_html}{title}</h3>
            <p style="margin:0; color: {get_theme()['text_secondary']};">{content}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: str | int):
    """Render a polished metric card."""
    st.markdown(
        f"""
        <div class="nexus-metric">
            <div class="value">{value}</div>
            <div style="font-size:0.875rem; color:{get_theme()['text_muted']}; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(status: str, text: str):
    """Render a colored status badge."""
    # Use simple colors based on status
    theme = get_theme()
    colors = {
        "success": theme["success"],
        "warning": theme["warning"],
        "danger": theme["danger"],
        "info": theme["info"]
    }
    color = colors.get(status, theme["text_muted"])
    st.markdown(
        f"""
        <span style="background:{color}22; color:{color}; padding:2px 10px; border-radius:99px; font-size:0.75rem; font-weight:700; border:1px solid {color}44;">
            {text}
        </span>
        """,
        unsafe_allow_html=True
    )


def render_chat_message(role: str, content: str):
    """Render a chat bubble."""
    bubble_class = "user-bubble" if role == "user" else "ai-bubble"
    st.markdown(
        f'<div class="chat-bubble {bubble_class}">{content}</div>',
        unsafe_allow_html=True,
    )