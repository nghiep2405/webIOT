import streamlit as st
from mqttService import mqtt_client
import datetime

def send_motion_schedule_string(start_time: str, end_time: str):
    try:
        time_range_str = f"{start_time}-{end_time}"
        mqtt_client.publish("motion/notification/time_rangeeeee", time_range_str, qos=1)
        st.success(f"Anti-theft time sent: {time_range_str}")
    except Exception as e:
        st.error(f"Error sending anti-theft time: {e}")


def security_controlUI():
    st.subheader("🕓 Anti-theft Time Settings (ESP32)")

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("Start Time", value=datetime.time(10, 0), step=datetime.timedelta(minutes=1), key="alarm_start")
    with col2:
        end_time = st.time_input("End Time", value=datetime.time(13, 0), step=datetime.timedelta(minutes=1), key="alarm_end")

    if st.button("Send Anti-theft Time"):
        if start_time and end_time:
            start_str = start_time.strftime("%H:%M")
            end_str = end_time.strftime("%H:%M") 
            send_motion_schedule_string(start_str, end_str)
    else:
        st.warning("Please enter both start and end times.")

security_controlUI()