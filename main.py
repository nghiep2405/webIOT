
import streamlit as st
from pages.login_register.login import login_ui 
from pages.login_register.register import register_ui
from pages.chatbot.chatbot import chat

if st.query_params.get("logout") == "true":
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    if st.user.is_logged_in:
        st.logout()
    st.markdown("""
        <script>
        document.cookie.split(";").forEach(function(c) { 
            document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
        });
        localStorage.clear();
        sessionStorage.clear();
        </script>
    """, unsafe_allow_html=True)
    st.query_params.clear()
    st.rerun()

logged_in = st.session_state.get("logged_in", False)
current_page = st.session_state.get("page", "login")

if logged_in:
    st.set_page_config(page_title="IoT", layout="wide")
else:
    if current_page == "login" or current_page == "register":
        st.set_page_config(page_title="IoT", layout="centered")
    else:
        st.set_page_config(page_title="IoT", layout="wide")

if st.user.is_logged_in and not st.session_state.get("logged_in", False):
    st.session_state.logged_in = True
    st.session_state.user_name = st.user.name
    st.session_state.user_email = getattr(st.user, 'email', '')
    st.session_state.user_picture = getattr(st.user, 'picture', '')
    st.session_state.login_method = "google"
    st.session_state.page = "main"
    st.rerun()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_picture" not in st.session_state:
    st.session_state.user_picture = ""
if "page" not in st.session_state:
    st.session_state.page = "login"
if "login_method" not in st.session_state:
    st.session_state.login_method = ""

st.markdown("""
    <style>
    .st-key-no_style .stButton > button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: none;
        background-color: #FF4B4B;
        color: #FAFAFA;
        font-size: 24px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.1s ease, box-shadow 0.2s ease;
    }
    .st-key-no_style .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transform: scale(1.05);
    }
    .st-key-no_style .stButton > button:active {
        transform: scale(0.95);
    }
    .sidebar-user-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0 0 1rem 0;
        color: white;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
    }
    .sidebar-user-name {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        word-break: break-word;
    }
    .sidebar-user-email {
        font-size: 0.8rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
        word-break: break-word;
    }
    .sidebar-login-method {
        font-size: 0.8rem;
        opacity: 0.9;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        display: inline-block;
    }
    .user-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: 3px solid rgba(255, 255, 255, 0.3);
        margin: 0 auto 0.5rem auto;
        display: block;
        object-fit: cover;
    }
    </style>
""", unsafe_allow_html=True)

pages = [
    st.Page("pages/live_cam/live_cam.py", title="Live cam"),
    st.Page("pages/control/control.py", title="Control"),
    st.Page("pages/statistic/statistic.py", title="Statistic"),
    st.Page("pages/overview/overview.py", title="About us"),
]

if st.session_state.logged_in:
    with st.sidebar:
        user_info_html = "<div class='sidebar-user-info'>"
        if st.session_state.login_method == "google" and st.session_state.user_picture:
            user_info_html += f'<img src="{st.session_state.user_picture}" class="user-avatar" alt="Avatar">'
        else:
            user_info_html += '<div style="font-size: 2rem; margin-bottom: 0.5rem;">👤</div>'
        user_info_html += f"<div class='sidebar-user-name'>{st.session_state.user_name}</div>"
        if st.session_state.login_method == "google":
            if st.session_state.user_email:
                user_info_html += f"<div class='sidebar-user-email'>{st.session_state.user_email}</div>"
        user_info_html += "</div>"
        st.markdown(user_info_html, unsafe_allow_html=True)

        nav = st.navigation(pages)
        st.markdown("---")
        st.markdown("<div style='flex: 1;'></div>", unsafe_allow_html=True)
        st.markdown('<div style="width: 100%; padding: 0; margin: 0;">', unsafe_allow_html=True)
        if st.button("🚪 Log out", key="sidebar_logout", use_container_width=True):
            st.query_params["logout"] = "true"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([15,1], vertical_alignment="top")
    with left:
        with st.container(height=600, border=False):
            nav.run()
    with right:
        bot1, bot2 = st.columns([1,20], vertical_alignment="bottom")
        bot1.container(height=600, border=False)
        if bot2.button("",icon=":material/support_agent:", use_container_width=True, type="primary", key="no_style"):
            chat()
else:
    if st.session_state.page == "login":
        login_ui()
    elif st.session_state.page == "register":
        register_ui()
