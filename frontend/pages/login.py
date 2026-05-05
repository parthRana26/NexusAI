"""
pages/login.py — Login Page
"""

import streamlit as st
from components import init_page, render_auth_container, render_sidebar
from api_client import login, NexusAPIError
from styles import get_theme

st.set_page_config(page_title="Login — NexusAI", page_icon="🔐", layout="centered", initial_sidebar_state="expanded")

# Init
init_page("Login")
render_sidebar()

# UI
render_auth_container("Welcome Back", "Sign in to access your intelligence platform.")

col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown(
                f'<p style="font-size:1.25rem;font-weight:700;margin-bottom:1.5rem;color:{get_theme()["text_primary"]};">Member Login</p>',
                unsafe_allow_html=True,
            )

            email = st.text_input("Email Address", placeholder="name@company.com")
            password = st.text_input("Security Password", type="password", placeholder="••••••••")

            submitted = st.form_submit_button("Sign In to NexusAI", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Credential fields are required.")
                else:
                    with st.spinner("Verifying identity..."):
                        try:
                            login(email, password)
                            st.success("Identity verified.")
                            st.switch_page("app.py")
                        except NexusAPIError as e:
                            st.error(f"Authentication failed: {e}")
                        except Exception as e:
                            st.error(f"System error: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<p style="text-align:center; color:{get_theme()["text_secondary"]}; font-size:0.9rem;">New to NexusAI?</p>',
            unsafe_allow_html=True
        )
        if st.button("Create Corporate Account", key="goto_reg", use_container_width=True, type="secondary"):
            st.switch_page("pages/register.py")

# Theme toggle
st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
col_a, col_b, col_c = st.columns([2, 2, 2])
with col_b:
    from styles import toggle_theme
    is_dark = st.session_state.get("theme") == "dark"
    if st.button(f"{'🌙' if not is_dark else '☀️'} Mode", key="login_theme", use_container_width=True, type="secondary"):
        toggle_theme()