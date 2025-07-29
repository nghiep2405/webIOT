import streamlit as st
import requests

def register_ui():
    st.title("📝 Register")
    name = st.text_input("User Name", key="registerName")
    password = st.text_input("Password", type="password", key="registerPassword")

    if st.button("Register"):
        res = requests.post("http://localhost:8000/register", params={"name": name, "password": password})
        if res.status_code == 200:
            st.success("Registration successful! Please go back to the login page.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Registration failed")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()
