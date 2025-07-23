import streamlit as st
import requests

def register_ui():
    st.title("📝 Register")
    name = st.text_input("User Name", key="registerName")
    password = st.text_input("Password", type="password", key="registerPassword")

    if st.button("Register"):
        res = requests.post("http://localhost:8000/register", params={"name": name, "password": password})
        if res.status_code == 200:
            st.success("Registration successful! Quay lại trang đăng nhập.")
            st.session_state.page = "login"
        else:
            st.error("Registration failed")

    if st.button("Quay lại đăng nhập"):
        st.session_state.page = "login"
        st.rerun()