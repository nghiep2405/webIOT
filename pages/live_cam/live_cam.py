import streamlit as st

# URL stream MJPEG từ ESP32-CAM
ESP32_STREAM_URL = "http://192.168.217.184:81/stream"  # Thay bằng IP thật của bạn

st.title("Live View")

st.markdown(
    f"""
    <div style="text-align:center;">
        <iframe src="{ESP32_STREAM_URL}" width="640" height="480" />
    </div>
    """,
    unsafe_allow_html=True
)


