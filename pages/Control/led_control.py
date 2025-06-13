import streamlit as st
from mqttService import mqtt_client

def led_controlUI():
    st.subheader("🔴 Điều khiển LED (ESP32)")

led_controlUI()