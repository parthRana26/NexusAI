"""
components.py — Shared UI Components for NexusAI
Centralized logic for sidebar, headers, and premium cards.
"""

import streamlit as st
from styles import apply_theme, get_theme, toggle_theme
from api_client import logout, get_chat_sessions

# ── Constants ──────────────────────────────────────────
NAV_ITEMS = [
    ("🏠 Dashboard", "pages/dashboard.py"),
    ("💬 Chat", "pages/chat.py"),
    ("📄 Document Chat", "pages/document_chat.py"),
    ("🧰 AI Tools", "pages/tools.py"),
    ("👤 Profile", "pages/profile.py"),
]

def init_page(title: str, icon: str = "🧠"):
    """Initialize page theme and config."""
    # This must be the first Streamlit command called on any page
    # Note: st.set_page_config can only be called once and must be at the top level usually.
    # We will handle it in individual pages for now but use this for other init.
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
    apply_theme()

def render_sidebar():
    """Render the premium sidebar with navigation and user info."""
    theme = get_theme()
    is_dark = st.session_state.get("theme") == "dark"
    theme_icon = "🌙" if not is_dark else "☀️"
    theme_label = "Dark Mode" if not is_dark else "Light Mode"

    with st.sidebar:
        # Logo
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:2rem;padding:0.5rem 0;">
                <span style="font-size:2.5rem;">🧠</span>
                <div>
                    <h2 style="margin:0;font-size:1.5rem;font-weight:800;letter-spacing:-0.04em;color:{theme['text_primary']};">NexusAI</h2>
                    <p style="margin:0;font-size:0.75rem;color:{theme['text_muted']};font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">Pro Edition</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Theme toggle button
        st.button(
            f"{theme_icon} {theme_label}",
            key="sidebar_theme_toggle_global",
            on_click=toggle_theme,
            use_container_width=True,
            type="secondary",
        )

        st.divider()

        # Navigation
        st.markdown(
            f'<p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;color:{theme["text_muted"]};font-weight:800;margin-bottom:0.75rem;opacity:0.8;">Navigation</p>',
            unsafe_allow_html=True,
        )

        # Build dynamic nav list
        current_nav = NAV_ITEMS.copy()
        user = st.session_state.get("user", {})
        role = user.get("role", "user") if isinstance(user, dict) else "user"
        if role == "admin":
            current_nav.append(("⚙️ Admin Panel", "pages/admin.py"))

        for label, page_path in current_nav:
            st.page_link(page_path, label=label, use_container_width=True)

        st.divider()

        # Session History (Sidebar)
        col_h1, col_h2 = st.columns([2, 1])
        with col_h1:
            st.markdown(
                f'<p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;color:{theme["text_muted"]};font-weight:800;margin-top:0.4rem;opacity:0.8;">Recent Chats</p>',
                unsafe_allow_html=True,
            )
        with col_h2:
            if st.button("➕ New", key="new_chat_sidebar", use_container_width=True, type="primary"):
                st.session_state.pop("current_session_id", None)
                st.session_state["chat_history"] = []
                st.switch_page("pages/chat.py")

        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        
        try:
            sessions = get_chat_sessions()
            if sessions:
                for s in sessions[:10]: # Show last 10
                    title = s['title']
                    if len(title) > 25:
                        title = title[:22] + "..."
                    
                    if st.button(f"📄 {title}", key=f"sid_{s['id']}", use_container_width=True, help=f"Created: {s['created_at']}"):
                        st.session_state["current_session_id"] = s["id"]
                        st.session_state["chat_history"] = [] # Trigger reload
                        st.switch_page("pages/chat.py")
            else:
                st.markdown(f'<p style="font-size:0.75rem;color:{theme["text_muted"]};padding-left:0.5rem;">No active sessions</p>', unsafe_allow_html=True)
        except Exception:
            st.markdown(f'<p style="font-size:0.75rem;color:{theme["danger"]};padding-left:0.5rem;">Failed to load sessions</p>', unsafe_allow_html=True)

        st.divider()

        # User mini-card
        user = st.session_state.get("user")
        if user and isinstance(user, dict):
            name = user.get("full_name") or user.get("name", "User")
            email = user.get("email", "")
            role_label = user.get("role", "user").capitalize()
            st.markdown(
                f"""
                <div style="padding:1rem;border-radius:14px;background-color:{theme['bg_tertiary']};border:1px solid {theme['border']};margin-bottom:1rem;transition:all 0.3s ease;">
                    <p style="margin:0;font-weight:700;font-size:0.9rem;color:{theme['text_primary']};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</p>
                    <p style="margin:0.2rem 0 0.6rem 0;font-size:0.75rem;color:{theme['text_muted']};white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{email}</p>
                    <span style="background:{theme['accent']}22; color:{theme['accent']}; font-size:0.65rem; font-weight:700; padding:3px 10px; border-radius:6px; border:1px solid {theme['accent']}44;">{role_label}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Logout
        if st.button("🚪 Sign Out", key="sidebar_logout_global", use_container_width=True, type="secondary"):
            logout()
            st.rerun()

        st.markdown(
            f'<p style="font-size:0.65rem;color:{theme["text_muted"]};text-align:center;margin-top:2rem;opacity:0.6;">NexusAI v1.2.0 • Production Ready</p>',
            unsafe_allow_html=True,
        )

def render_page_header(title: str, subtitle: str = ""):
    """Render a premium page header."""
    theme = get_theme()
    st.markdown(
        f"""
        <div style="margin-bottom:2.5rem;">
            <h1 style="margin:0;font-size:2.5rem;font-weight:800;letter-spacing:-0.04em;">{title}</h1>
            {f'<p style="margin:0.5rem 0 0 0;font-size:1.1rem;color:{theme["text_secondary"]};">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_auth_container(title: str, subtitle: str = ""):
    """Render the auth form container."""
    theme = get_theme()
    st.markdown(
        f"""
        <div style="text-align:center;margin-bottom:2.5rem;">
            <span style="font-size:4rem;">🧠</span>
            <h1 style="margin:1rem 0 0 0;font-weight:800;font-size:2.25rem;letter-spacing:-0.04em;">NexusAI</h1>
            <p style="color:{theme['text_secondary']};font-size:1.1rem;margin-top:0.5rem;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
