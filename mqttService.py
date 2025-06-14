import paho.mqtt.client as mqtt
import streamlit as st

# MQTT configuration
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_PIR_TOPIC = "sensor/pir"
MQTT_CAMERA_IP_TOPIC = "esp32/camera_ip"
MQTT_MOTION_SCHEDULE_TOPIC = "motion/notification/time_range"
MQTT_SONG_TOPIC = "audio/play"

# Initialize MQTT client
mqtt_client = mqtt.Client(client_id="", protocol=mqtt.MQTTv311)

def connect_mqtt(): 
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        #st.success("Connected to MQTT broker!")
    except Exception as e:
        st.error(f"Failed to connect to MQTT broker: {e}")

connect_mqtt()