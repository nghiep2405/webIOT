import streamlit as st
from mqttService import mqtt_client
import datetime

def send_motion_schedule_string(start_time: str, end_time: str):
    try:
        time_range_str = f"{start_time}-{end_time}"
        mqtt_client.publish("motion/notification/time_range", time_range_str, qos=1)
        st.success(f"Đã gửi thời gian chống trộm: {time_range_str}")
    except Exception as e:
        st.error(f"Lỗi khi gửi thời gian chống trộm: {e}")


def security_controlUI():
    st.subheader("🕓 Cài đặt thời gian chống trộm (ESP32)")

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("Giờ bắt đầu", value=datetime.time(10, 0), step=datetime.timedelta(minutes=1), key="alarm_start")
    with col2:
        end_time = st.time_input("Giờ kết thúc", value=datetime.time(13, 0), step=datetime.timedelta(minutes=1), key="alarm_end")

    if st.button("Gửi thời gian chống trộm"):
        if start_time and end_time:
            start_str = start_time.strftime("%H:%M")
            end_str = end_time.strftime("%H:%M") 
            send_motion_schedule_string(start_str, end_str)
    else:
        st.warning("Vui lòng nhập đầy đủ giờ bắt đầu và kết thúc.")

security_controlUI()