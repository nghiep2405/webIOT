import streamlit as st
import pandas as pd
import requests

# URL stream MJPEG từ ESP32-CAM
ESP32_STREAM_URL = "http://192.168.1.7"  # Doi wifi thi xem lai o tren ESP32 - CAM

st.title("Live View")

left, right = st.columns([2,1], vertical_alignment="top")

with left:
    st.markdown(
        f"""
        <div style="text-align:center;">
            <iframe src="{ESP32_STREAM_URL}" width="680" height="480" />
        </div>
        """,
        unsafe_allow_html=True
    )

if "enter" not in st.session_state:
    st.session_state.enter = {"Timestamp":[]}

@st.fragment(run_every=5)
def people_enter():
    # Gửi yêu cầu GET và lấy phản hồi
    response = requests.get("http://127.0.0.1:8000/get_enter").json()
    
    # Thêm thời gian vào danh sách
    st.session_state.enter["Timestamp"].extend(response["Timestamp"])

    # Giới hạn số lượng mục
    if len(st.session_state.enter["Timestamp"]) > 200:
        st.session_state.enter["Timestamp"] = st.session_state.enter["Timestamp"][100:]

    # Chuyển đổi danh sách thời gian sang DataFrame
    time_data = pd.DataFrame(st.session_state.enter)
    
    # Định dạng cột thời gian
    time_data['Timestamp'] = pd.to_datetime(time_data['Timestamp'])

    # Hiển thị DataFrame đã định dạng
    st.dataframe(time_data, width=300, height=500)

with right:
    people_enter()



