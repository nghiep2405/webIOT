import streamlit as st
import pandas as pd
import requests

# URL stream MJPEG từ ESP32-CAM
ESP32_STREAM_URL = "http://172.20.10.3"  # Thay bằng IP thật của bạn

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
    st.session_state.enter = {"time":[]}

@st.fragment(run_every=5)
def people_enter():
    response = requests.get(f"http://127.0.0.1:8000/get_enter").json()
    st.session_state.enter["time"].extend(response["time"])
    if len(st.session_state.enter["time"]) > 200:
        st.session_state.enter["time"] = st.session_state.enter["time"][100:]

    st.dataframe(pd.DataFrame(st.session_state.enter), width=300, height=500)

with right:
    people_enter()



