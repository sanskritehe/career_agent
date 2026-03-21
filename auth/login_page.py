"""
auth/login_page.py
------------------
Streamlit login / register UI.
Renders a full-page auth screen when the user is not logged in.
"""

import streamlit as st
from auth.auth import register_user, login_user
from utils.database import update_user_profile


def render_auth_page():
    """
    Full-page login/register screen.
    Sets st.session_state.user on success and triggers st.rerun().
    """
    # ── Page style ─────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0f1e 0%, #0f172a 50%, #0a0f1e 100%);
    }
    [data-testid="stSidebar"] { display: none; }
    div[data-testid="stForm"] {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 2rem;
    }
    .stTextInput input {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px #6366f133 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 2.5rem 0 1.5rem 0;">
        <div style="font-size:3rem; margin-bottom:0.5rem;">🎯</div>
        <h1 style="color:#e2e8f0; font-size:2rem; margin:0; font-weight:800;">
            Career AI Assistant
        </h1>
        <p style="color:#64748b; font-size:0.95rem; margin-top:0.5rem;">
            Your personalised interview prep and career growth platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ────────────────────────────────────────────────────────────────────
    _, center, _ = st.columns([1, 1.4, 1])

    with center:
        tab_login, tab_register = st.tabs(["🔑  Login", "✨  Register"])

        # ── LOGIN ───────────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                st.markdown(
                    '<p style="color:#94a3b8; font-size:0.85rem; margin-bottom:1rem;">'
                    'Enter your username or email to continue.</p>',
                    unsafe_allow_html=True,
                )
                username_or_email = st.text_input(
                    "Username or Email",
                    placeholder="yourname or you@email.com",
                    key="login_identifier",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••",
                    key="login_password",
                )
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button(
                    "Login →",
                    use_container_width=True,
                    type="primary",
                )

            if submitted:
                if not username_or_email or not password:
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Logging in..."):
                        success, msg, user = login_user(username_or_email, password)
                    if success:
                        st.success(msg)
                        st.session_state.user = user
                        st.session_state.user_id = user["id"]
                        st.rerun()
                    else:
                        st.error(msg)

        # ── REGISTER ────────────────────────────────────────────────────────────
        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("register_form", clear_on_submit=True):
                st.markdown(
                    '<p style="color:#94a3b8; font-size:0.85rem; margin-bottom:1rem;">'
                    'Create your free account to save your progress.</p>',
                    unsafe_allow_html=True,
                )
                full_name = st.text_input(
                    "Full Name",
                    placeholder="Samyuktha Sundar",
                    key="reg_fullname",
                )
                reg_username = st.text_input(
                    "Username",
                    placeholder="samyuktha123",
                    key="reg_username",
                    help="3-30 characters, letters/numbers/underscores only",
                )
                reg_email = st.text_input(
                    "Email",
                    placeholder="you@email.com",
                    key="reg_email",
                )
                reg_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Min. 6 characters",
                    key="reg_password",
                )
                reg_password2 = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Repeat your password",
                    key="reg_password2",
                )
                st.markdown("<br>", unsafe_allow_html=True)
                reg_submitted = st.form_submit_button(
                    "Create Account →",
                    use_container_width=True,
                    type="primary",
                )

            if reg_submitted:
                if not all([full_name, reg_username, reg_email, reg_password, reg_password2]):
                    st.error("Please fill in all fields.")
                elif reg_password != reg_password2:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Creating your account..."):
                        success, msg = register_user(reg_username, reg_email, reg_password, full_name)
                    if success:
                        st.success(f"✅ {msg} You can now log in.")
                    else:
                        st.error(msg)

    # ── Footer ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; margin-top:3rem; color:#334155; font-size:0.78rem;">
        Powered by Groq LLaMA 3.3 &nbsp;&#183;&nbsp; Built with Streamlit
    </div>
    """, unsafe_allow_html=True)