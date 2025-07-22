import streamlit as st
import streamlit.components.v1 as components

@st.dialog("Support Agent")
def chat():
    iframe_src = "https://www.chatbase.co/chatbot-iframe/4GdZAgF-QDxeZqrOkYhSb"
    components.iframe(
        src=iframe_src,
        width=600,         # bạn có thể điều chỉnh
        height=700,        # phù hợp với nội dung iframe
        scrolling=True
    )