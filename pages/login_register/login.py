import streamlit as st
import requests

def login_ui():
    print("Rendering login UI...")
    st.title("🔐 Login")

    # Check and show message if just logged out
    if st.query_params.get("logout") == "true":
        st.success("Successfully logged out!")
        st.query_params.clear()

    # Tabs to select login method
    tab1, tab2 = st.tabs(["🔑 Username & Password", "🌐 Login with Google"])
    
    with tab1:
        st.subheader("Login with your account")
        
        # Get user input
        name = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")

        # Login with username-password
        if st.button("Login", key="btn_login", use_container_width=True):
            if not name or not password:
                st.warning("Please enter both username and password.")
            else:
                try:
                    res = requests.post("http://localhost:8000/login", params={"name": name, "password": password})
                    if res.status_code == 200:
                        st.session_state.logged_in = True
                        st.session_state.user_name = name
                        st.session_state.user_email = ""  # No email for username/password
                        st.session_state.user_picture = ""  # No picture for username/password
                        st.session_state.login_method = "username/password"
                        st.session_state.page = "main"
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Login failed. Please check your credentials.")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to server. Please try again later.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    with tab2:
        st.subheader("Login with Google")
        
        # Check Google login status
        if st.user.is_logged_in:
            st.info(f"Logged in with Google account: **{st.user.name}**")
            
            # Show avatar if available
            if hasattr(st.user, 'picture') and st.user.picture:
                col_avatar, col_info = st.columns([1, 3])
                with col_avatar:
                    st.image(st.user.picture, width=80)
                with col_info:
                    st.write(f"**Name:** {st.user.name}")
                    if hasattr(st.user, 'email') and st.user.email:
                        st.write(f"**Email:** {st.user.email}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Continue with this account", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.user_name = st.user.name
                    st.session_state.user_email = getattr(st.user, 'email', '')
                    st.session_state.user_picture = getattr(st.user, 'picture', '')
                    st.session_state.login_method = "google"
                    st.session_state.page = "main"
                    st.rerun()
            
            with col2:
                if st.button("🔄 Switch Google account", use_container_width=True):
                    # Logout from Google and login again
                    st.logout()
                    st.rerun()
        else:
            st.info("Quick and secure login with your Google account.")
            
            if st.button("🚀 Login with Google", use_container_width=True, type="primary"):
                # Login with Google
                st.login("google")

    # Divider and registration link
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("**Don't have an account?**")
    with col2:
        if st.button("📝 Register now", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

    # Handle Google OAuth callback
    if st.user.is_logged_in and not st.session_state.get("logged_in", False):
        if st.user.name:
            st.session_state.logged_in = True
            st.session_state.user_name = st.user.name
            st.session_state.user_email = getattr(st.user, 'email', '')
            st.session_state.user_picture = getattr(st.user, 'picture', '')
            st.session_state.login_method = "google"
            st.session_state.page = "main"
            st.rerun()
