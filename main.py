import streamlit as st
from pages.login_register.login import login_ui 
from pages.login_register.register import register_ui
from pages.chatbot.chatbot import chat

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
    st.session_state.page = "main"
    st.experimental_rerun()

# Initialize Session State for necessary variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "page" not in st.session_state:
    st.session_state.page = "login"


st.markdown("""
    <style>
    /* Bỏ style cho nút ngoại lệ */
    .st-key-no_style .stButton > button {
        /* Hoặc chỉ định lại kiểu bạn muốn: */
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
    </style>
    """, 
    unsafe_allow_html=True
)


# Define page navigation
pages = [
    st.Page("pages/overview/overview.py", title="Overview"),
    st.Page("pages/live_cam/live_cam.py", title="Live cam"),
    st.Page("pages/control/control.py", title="Control"),
    st.Page("pages/statistic/statistic.py", title="Statistic"),
]

# If logged in, show navigation; else show login/register
if st.session_state.logged_in:
    left, right = st.columns([15,1], vertical_alignment="top")

    with left:
        with st.container(height=700, border=False):
            nav = st.navigation(pages)
            nav.run()
    with right:
        bot1, bot2 = st.columns([1,20], vertical_alignment="bottom")
        bot1.container(height=700, border=False)
        if bot2.button("",icon=":material/support_agent:", use_container_width=True, type="primary", key="no_style"):
            chat()
else:
    if st.session_state.page == "login":
        login_ui()
    elif st.session_state.page == "register":
        register_ui()