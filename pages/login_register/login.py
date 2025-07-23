import streamlit as st
import requests

def login_ui():
    print("Rendering login UI...")
    st.title("🔐 Login")

    # Lấy input người dùng
    name = st.text_input("User Name")
    password = st.text_input("Password", type="password")

    # Login bằng username-password
    if st.button("Login", key="btn_login"):
        if not name or not password:
            st.warning("Please enter both name and password.")
        else:
            res = requests.post("http://localhost:8000/login", params={"name": name, "password": password})
            if res.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.session_state.page = "main"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Login failed")

    # Nếu chưa login thì hiện nút login với Google (giả định bạn dùng Firebase hoặc OAuth sau)
    if not st.session_state.get("logged_in", False):
        st.markdown("---")
        st.info("Or log in with Google:")
        if st.button("Log in with Google"):
            st.login("google")
            st.json(st.user)
        
    if st.user.is_logged_in and not st.session_state.get("logged_in", False):
        st.session_state.logged_in = True
        st.session_state.user_name = st.user.name
        st.markdown(f"✅ Welcome, **{st.session_state.user_name}**!")
        st.session_state.page = "main"
        st.experimental_rerun()

    if st.button("Chưa có tài khoản? Đăng ký"):
        st.session_state.page = "register"
        st.rerun()