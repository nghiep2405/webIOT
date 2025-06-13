import streamlit as st
from pages.login_register.login import login_ui 
from pages.login_register.register import register_ui

st.set_page_config(page_title="IoT", layout="wide")

# Initialize Session State for necessary variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

# Define page navigation
pages = [st.Page("pages/live_cam/live_cam.py", title="Live cam"),
         st.Page("pages/control/control.py", title="Control"),
         st.Page("pages/statistic/statistic.py", title="Statistic"),
         st.Page("pages/chatbot/chatbot.py", title="Chatbot")]

# If logged in, show navigation; else show login/register
if st.session_state.logged_in:
    nav = st.navigation(pages)
    nav.run()
else:
    if st.session_state.page == "login":
        login_ui()
    elif st.session_state.page == "register":
        register_ui()