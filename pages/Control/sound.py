import streamlit as st
import requests
from mqttService import mqtt_client, MQTT_SONG_TOPIC
import pandas as pd

PLAYLIST_FILE = "playlist.txt"
API_BASE_URL = "http://localhost:8000"

def load_playlist():
    try:
        with open(PLAYLIST_FILE, "r") as file:
            files = [line.strip() for line in file.readlines() if line.strip()]
        custom_names = ["Làm việc đi", "Hết giờ làm việc", "Báo cáo", "Có trộm đột nhập"]
        return list(zip(files, custom_names[:len(files)]))
    except FileNotFoundError:
        st.error("File playlist.txt not found! Please create it.")
        return []
    except Exception as e:
        st.error(f"Error reading playlist.txt: {e}")
        return []

def save_sound_history(user_name, sound_name):
    try:
        response = requests.post(
            f"{API_BASE_URL}/save-sound-history",
            json={"user_name": user_name, "sound_name": sound_name}
        )
        if response.status_code == 200:
            return True, response.json().get("timestamp", "")
        else:
            st.error(f"Lỗi lưu lịch sử: {response.text}")
            return False, ""
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return False, ""

def sound_controlUI():
    st.subheader("🔔 Chọn Bản Ghi Âm Để Phát")
    
    if not st.session_state.get("logged_in", False):
        st.error("Vui lòng đăng nhập để sử dụng chức năng này!")
        return

    user_name = st.session_state.get("user_name", "")
    if not user_name:
        st.error("Không thể xác định tài khoản người dùng!")
        return

    st.write("Bạn có thể chọn bản ghi âm để phát.")

    audio_files = load_playlist()
    messages = []  # Danh sách chứa các thông báo

    if audio_files:
        cols = st.columns(2)
        for idx, (file, display_name) in enumerate(audio_files, 1):
            with cols[(idx - 1) % 2]:
                if st.button(f"{display_name}", key=f"play_{idx}"):
                    try:
                        mqtt_client.publish(MQTT_SONG_TOPIC, str(idx), qos=1)
                        success, timestamp = save_sound_history(user_name, display_name)
                        messages.append(f"🔊 Đang gửi lệnh phát {file}")
                        if success:
                            messages.append(f"✅ Đang phát: {display_name}")
                            messages.append(f"📝 Đã ghi lại lịch sử lúc: {timestamp}")
                        else:
                            messages.append("⚠️ Không thể lưu lịch sử, nhưng âm thanh vẫn được phát")
                    except Exception as e:
                        messages.append(f"❌ Lỗi khi phát {display_name}: {e}")
    else:
        st.warning("No audio files found in playlist.txt!")

    # Hiển thị các thông báo ở dưới cùng
    st.divider()
    for msg in messages:
        if msg.startswith("✅"):
            st.success(msg)
        elif msg.startswith("⚠️") or msg.startswith("❌"):
            st.warning(msg)
        elif msg.startswith("📝"):
            st.info(msg)
        else:
            st.success(msg)

    # Thêm chú thích cuối trang
    st.info("💡 **Lưu ý:** Để xem thống kê và lịch sử sử dụng âm thanh, vui lòng truy cập trang **Statistics**.")

# Chạy giao diện
sound_controlUI()
