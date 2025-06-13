import streamlit as st

st.title("Control Panel")

tab1, tab2, tab3 = st.tabs(["🔴 LED Control", "🔔 Buzzer Control", "🔒 Security Control"])

with tab1:
    exec(open("pages/Control/led_control.py",  encoding="utf-8").read())

with tab2:
    exec(open("pages/Control/buzzer.py",  encoding="utf-8").read())

with tab3:
    exec(open("pages/Control/security.py",  encoding="utf-8").read())
