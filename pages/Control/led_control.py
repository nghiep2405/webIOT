import streamlit as st
import requests

def led_controlUI():
    st.subheader("💡 Control LED (ESP32)")

    # Thêm CSS tùy chỉnh - chỉ áp dụng cho LED control section
    st.markdown(
        """
        <style>
        /* CSS chỉ áp dụng cho slider và các element cụ thể */
        .stSlider {
            max-width: 950px;  /* Giới hạn chiều dài thanh slider */
            margin: auto;      /* Căn giữa thanh slider */
        }
        .stSlider > div > div > div {
            background-color: #ff3333;
            border-radius: 10px;
        }
        
        /* CSS cho LED control buttons - sử dụng key cụ thể */
        .st-key-led_brightness_btn .stButton>button {
            background-color: #ff3333;
            color: white;
            border-radius: 20px;
            padding: 10px 20px;
            border: none;
            font-size: 16px;
            margin: 5px;
        }
        .st-key-led_brightness_btn .stButton>button:hover {
            background-color: #cc0000;
        }
        
        /* CSS cho expander info */
        .led-info-section {
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Thêm thanh trượt để điều chỉnh độ sáng LED
    led_intensity = st.slider("LED Brightness", 0, 255, 0)

    # Doi wifi thi xem lai o tren ESP32 - CAM
    esp32_ip = "http://192.168.1.7"

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

    # Thêm một số thông tin bổ sung
    with st.expander("ℹ️ Information ESP32"):
        st.markdown(f"""
        <div class="led-info-section">
            <strong>📡 IP Address:</strong> {esp32_ip}<br><br>
            <strong>🔗 Status:</strong> {'🟢 Connected' if st.session_state.get('prev_intensity', 0) >= 0 else '🔴 Disconnected'}<br><br>
            <strong>💡 Current Brightness:</strong> {led_intensity}/255 ({round(led_intensity/255*100, 1)}%)
        </div>
        """, unsafe_allow_html=True)
    
led_controlUI()