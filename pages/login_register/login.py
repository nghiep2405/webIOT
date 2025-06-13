import streamlit as st
import requests

def login_ui():
    st.title("🔐 Login")
    name = st.text_input("User Name", key="loginName")
    password = st.text_input("Password", type="password", key="loginPassword")

    if st.button("Login"):
        res = requests.post("http://localhost:8000/login", params={"name": name, "password": password})
        if res.status_code == 200:
            st.session_state.logged_in = True
            st.session_state.user_name = name
            st.session_state.page = "main"
            st.success("Login successful!")
        else:
            st.error("Login failed")

    if st.button("Chưa có tài khoản? Đăng ký"):
        st.session_state.page = "register"