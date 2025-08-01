import streamlit as st
import pandas as pd
import requests

# URL stream MJPEG từ ESP32-CAM
ESP32_STREAM_URL = "http://192.168.217.184:81/stream"  # Thay bằng IP thật của bạn

st.title("Live View")

left, right = st.columns([1,1], vertical_alignment="top")

with left:
    st.markdown(
        f"""
        <div style="text-align:center;">
            <iframe src="{ESP32_STREAM_URL}" width="500" height="480" />
        </div>
        """,
        unsafe_allow_html=True
    )

@st.fragment(run_every=5)
def people_enter():
    response = requests.get(f"http://127.0.0.1:8000/get_enter").json()
    st.table(pd.DataFrame(response))

with right:
    people_enter()



