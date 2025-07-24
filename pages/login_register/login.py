import streamlit as st
import requests

def login_ui():
    print("Rendering login UI...")
    st.title("🔐 Đăng nhập")

    # Kiểm tra và hiển thị thông báo nếu vừa logout
    if st.query_params.get("logout") == "true":
        st.success("Đã đăng xuất thành công!")
        st.query_params.clear()

    # Tab để chọn phương thức đăng nhập
    tab1, tab2 = st.tabs(["🔑 Tài khoản & Mật khẩu", "🌐 Đăng nhập Google"])
    
    with tab1:
        st.subheader("Đăng nhập bằng tài khoản")
        
        # Lấy input người dùng
        name = st.text_input("Tên đăng nhập", key="username_input")
        password = st.text_input("Mật khẩu", type="password", key="password_input")

        # Login bằng username-password
        if st.button("Đăng nhập", key="btn_login", use_container_width=True):
            if not name or not password:
                st.warning("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            else:
                try:
                    res = requests.post("http://localhost:8000/login", params={"name": name, "password": password})
                    if res.status_code == 200:
                        st.session_state.logged_in = True
                        st.session_state.user_name = name
                        st.session_state.login_method = "username/password"
                        st.session_state.page = "main"
                        st.success("Đăng nhập thành công!")
                        st.rerun()
                    else:
                        st.error("Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.")
                except requests.exceptions.ConnectionError:
                    st.error("Không thể kết nối đến server. Vui lòng thử lại sau.")
                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {str(e)}")

    with tab2:
        st.subheader("Đăng nhập bằng Google")
        
        # Kiểm tra trạng thái đăng nhập Google
        if st.user.is_logged_in:
            st.info(f"Đã đăng nhập Google với tài khoản: **{st.user.name}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Tiếp tục với tài khoản này", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.user_name = st.user.name
                    st.session_state.login_method = "google"
                    st.session_state.page = "main"
                    st.rerun()
            
            with col2:
                if st.button("🔄 Đổi tài khoản Google", use_container_width=True):
                    # Logout khỏi Google và đăng nhập lại
                    st.logout()
                    st.rerun()
        else:
            st.info("Đăng nhập nhanh chóng và an toàn với tài khoản Google của bạn.")
            
            if st.button("🚀 Đăng nhập với Google", use_container_width=True, type="primary"):
                # Đăng nhập với Google
                st.login("google")

    # Divider và link đăng ký
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("**Chưa có tài khoản?**")
    with col2:
        if st.button("📝 Đăng ký ngay", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

    # Xử lý khi Google OAuth hoàn thành (callback)
    if st.user.is_logged_in and not st.session_state.get("logged_in", False):
        if st.user.name:
            st.session_state.logged_in = True
            st.session_state.user_name = st.user.name
            st.session_state.login_method = "google"
            st.session_state.page = "main"
            st.rerun()