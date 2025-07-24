import streamlit as st
from pages.login_register.login import login_ui 
from pages.login_register.register import register_ui
from pages.chatbot.chatbot import chat

# Kiểm tra xem có yêu cầu logout không
if st.query_params.get("logout") == "true":
    # Xóa tất cả session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Logout khỏi Google OAuth
    if st.user.is_logged_in:
        st.logout()
    # Thêm JavaScript để xóa Google OAuth cookies/session
    st.markdown("""
        <script>
        // Xóa tất cả cookies liên quan đến Google OAuth
        document.cookie.split(";").forEach(function(c) { 
            document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
        });
        // Xóa localStorage và sessionStorage
        localStorage.clear();
        sessionStorage.clear();
        </script>
    """, unsafe_allow_html=True)
    # Xóa query params và reload
    st.query_params.clear()
    st.rerun()

# Kiểm tra trạng thái đăng nhập
logged_in = st.session_state.get("logged_in", False)
current_page = st.session_state.get("page", "login")

# Config trang theo trạng thái
if logged_in:
    st.set_page_config(page_title="IoT", layout="wide")
else:
    if current_page == "login" or current_page == "register":
        st.set_page_config(page_title="IoT", layout="centered")
    else:
        st.set_page_config(page_title="IoT", layout="wide")

# Xử lý đăng nhập Google OAuth
if st.user.is_logged_in and not st.session_state.get("logged_in", False):
    st.session_state.logged_in = True
    st.session_state.user_name = st.user.name
    st.session_state.login_method = "google"  # Đánh dấu phương thức đăng nhập
    st.session_state.page = "main"
    st.rerun()

# Initialize Session State cho các biến cần thiết
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "page" not in st.session_state:
    st.session_state.page = "login"
if "login_method" not in st.session_state:
    st.session_state.login_method = ""

# CSS styling
st.markdown("""
    <style>
    /* Style cho nút chatbot */
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
    
    /* Style cho nút logout trong sidebar - Fix position và prevent drift */
    .st-key-sidebar_logout .stButton > button {
        background-color: #dc3545 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2) !important;
        width: 100% !important;
        margin: 1rem 0 0 0 !important;
        position: relative !important;
        left: 0 !important;
        right: 0 !important;
        transform: none !important;
    }
    
    /* Fix sidebar button container */
    .st-key-sidebar_logout .stButton {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Ensure sidebar consistency */
    .css-1d391kg, .css-1rs6os, .css-17eq0hr {
        padding-right: 1rem !important;
        padding-left: 1rem !important;
    }
    .st-key-sidebar_logout .stButton > button:hover {
        background-color: #c82333;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
    }
    
    /* Style cho sidebar để đảm bảo consistent */
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
    }
    
    .sidebar-login-method {
        font-size: 0.8rem;
        opacity: 0.9;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        display: inline-block;
    }
    
    /* Style cho main header */
    .main-header {
        background: linear-gradient(90deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .main-title {
        color: #ffffff;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
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

# Nếu đã đăng nhập, hiện navigation với sidebar user info
if st.session_state.logged_in:
    # Sidebar với thông tin user
    with st.sidebar:
        # Thông tin user (bỏ icon điện thoại)
        st.markdown(f"""
            <div class="sidebar-user-info">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">👤</div>
                <div class="sidebar-user-name">{st.session_state.user_name}</div>
                <div class="sidebar-login-method">{st.session_state.login_method}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        nav = st.navigation(pages)
        
        # Divider
        st.markdown("---")
        
        # Spacer để đẩy nút logout xuống dưới
        st.markdown("<div style='flex: 1;'></div>", unsafe_allow_html=True)
        
        # Container cho nút logout để đảm bảo không bị lệch
        st.markdown('<div style="width: 100%; padding: 0; margin: 0;">', unsafe_allow_html=True)
        
        # Nút logout
        if st.button("🚪 Đăng xuất", key="sidebar_logout", use_container_width=True):
            # Set query params để trigger logout
            st.query_params["logout"] = "true"
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Bỏ main header để có thêm không gian
    
    # Main content với chatbot
    left, right = st.columns([15,1], vertical_alignment="top")

    with left:
        with st.container(height=600, border=False):
            nav.run()
    with right:
        bot1, bot2 = st.columns([1,20], vertical_alignment="bottom")
        bot1.container(height=600, border=False)
        if bot2.button("",icon=":material/support_agent:", use_container_width=True, type="primary", key="no_style"):
            chat()

# Nếu chưa đăng nhập, hiện trang login/register
else:
    if st.session_state.page == "login":
        login_ui()
    elif st.session_state.page == "register":
        register_ui()