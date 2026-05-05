"""
pages/register.py — Registration Page
"""

import streamlit as st
from components import init_page, render_auth_container, render_sidebar
from api_client import register, NexusAPIError
from styles import get_theme

st.set_page_config(page_title="Register — NexusAI", page_icon="📝", layout="centered", initial_sidebar_state="expanded")

# Init
init_page("Register")
render_sidebar()

# UI
render_auth_container("Get Started", "Create your secure NexusAI workspace.")

col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        with st.form("register_form", clear_on_submit=False):
            st.markdown(
                f'<p style="font-size:1.25rem;font-weight:700;margin-bottom:1.5rem;color:{get_theme()["text_primary"]};">Identity Setup</p>',
                unsafe_allow_html=True,
            )

            full_name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email Address", placeholder="name@company.com")
            password = st.text_input("Strong Password", type="password", placeholder="••••••••")
            confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")

            submitted = st.form_submit_button("Initialize Account", use_container_width=True)

            if submitted:
                if not all([full_name, email, password, confirm]):
                    st.error("All fields are mandatory.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    with st.spinner("Initializing..."):
                        try:
                            register(email, password, full_name)
                            st.success("Account ready for activation.")
                            st.switch_page("pages/login.py")
                        except NexusAPIError as e:
                            st.error(f"Setup failed: {e}")
                        except Exception as e:
                            st.error(f"System failure: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<p style="text-align:center; color:{get_theme()["text_secondary"]}; font-size:0.9rem;">Already have an account?</p>',
            unsafe_allow_html=True
        )
        if st.button("Sign In instead", key="goto_login", use_container_width=True, type="secondary"):
            st.switch_page("pages/login.py")

# Theme toggle
st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
col_a, col_b, col_c = st.columns([2, 2, 2])
with col_b:
    from styles import toggle_theme
    is_dark = st.session_state.get("theme") == "dark"
    if st.button(f"{'🌙' if not is_dark else '☀️'} Mode", key="reg_theme", use_container_width=True, type="secondary"):
        toggle_theme()