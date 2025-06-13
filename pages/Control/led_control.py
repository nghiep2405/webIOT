import streamlit as st
from mqttService import mqtt_client
import requests

def led_controlUI():
    st.subheader("🔴 Điều khiển LED (ESP32)")   

    # Thêm CSS tùy chỉnh
    st.markdown(
        """
        <style>
        .stButton>button {
            background-color: #ff3333;
            color: white;
            border-radius: 20px;
            padding: 10px 20px;
            border: none;
            font-size: 16px;
            margin: 5px;
        }
        .stButton>button:hover {
            background-color: #cc0000;
        }
        .stSlider > div > div > div {
            background-color: #ff3333;
            border-radius: 10px;
        }
        .stApp {
            background-color: #1a1a1a;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Thêm thanh trượt để điều chỉnh độ sáng LED
    led_intensity = st.slider("LED Brightness", 0, 255, 0)

    # URL của ESP32-CAM (thay bằng địa chỉ IP thực tế của bạn)
    esp32_ip = "http://192.168.217.184"

    # Gửi giá trị độ sáng đến ESP32-CAM khi thay đổi
    if 'prev_intensity' not in st.session_state:
        st.session_state.prev_intensity = 0

    if st.session_state.prev_intensity != led_intensity:
        url = f"{esp32_ip}/control?var=led_intensity&val={led_intensity}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                st.success(f"LED intensity set to {led_intensity}")
            else:
                st.error("Failed to set LED intensity")
        except Exception as e:
            st.error(f"Error connecting to ESP32-CAM: {e}")
        st.session_state.prev_intensity = led_intensity

led_controlUI()