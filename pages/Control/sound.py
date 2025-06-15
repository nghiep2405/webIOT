import streamlit as st
import requests
from mqttService import mqtt_client, MQTT_SONG_TOPIC
import pandas as pd

PLAYLIST_FILE = "playlist.txt"  # Place this file in the same directory as app.py or adjust path
API_BASE_URL = "http://localhost:8000"
# Read audio files from playlist.txt
def load_playlist():
    try:
        with open(PLAYLIST_FILE, "r") as file:
            # Read lines, strip whitespace, and filter empty lines
            files = [line.strip() for line in file.readlines() if line.strip()]
        custom_names = ["Làm việc đi", "Hết giờ làm việc", "Báo cáo", "Có trộm đột nhập"]
        return list(zip(files, custom_names[:len(files)]))  # Pair files with custom names
    except FileNotFoundError:
        st.error("File playlist.txt not found! Please create it.")
        return []
    except Exception as e:
        st.error(f"Error reading playlist.txt: {e}")
        return []

def save_sound_history(user_name, sound_name):
    """Lưu lịch sử sử dụng âm thanh vào database"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/save-sound-history",
            json={
                "user_name": user_name,
                "sound_name": sound_name
            }
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
    """Main function để gọi từ control.py"""
    # Load and display audio files
    st.subheader("🔔 Chọn Bản Ghi Âm Để Phát")
    # Kiểm tra xem user đã đăng nhập chưa
    if not st.session_state.get("logged_in", False):
        st.error("Vui lòng đăng nhập để sử dụng chức năng này!")
        return
    
    user_name = st.session_state.get("user_name", "")
    if not user_name:
        st.error("Không thể xác định tài khoản người dùng!")
        return
    
    st.write(f"Chào mừng, {user_name}! Bạn có thể chọn bản ghi âm để phát.")

    audio_files = load_playlist()
    if audio_files:
        cols = st.columns(2)  # Display 3 buttons per row, adjust as needed
        for idx, (file, display_name) in enumerate(audio_files, 1):
            with cols[(idx - 1) % 2]:
                if st.button(f"{display_name}", key=f"play_{idx}"):
                    try:
                        # Publish the file index to MQTT broker
                        mqtt_client.publish(MQTT_SONG_TOPIC, str(idx), qos=1)
                        # Lưu lịch sử sử dụng
                        success, timestamp = save_sound_history(user_name, display_name)
                        st.success(f"Đang gửi lệnh phát {file}")  
                        if success:
                            st.success(f"✅ Đang phát: {display_name}")
                            st.info(f"📝 Đã ghi lại lịch sử lúc: {timestamp}")
                        else:
                            st.success(f"🔊 Đang gửi lệnh phát {file}")
                            st.warning("⚠️ Không thể lưu lịch sử, nhưng âm thanh vẫn được phát")
                    except Exception as e:
                        st.error(f"❌ Lỗi khi phát {display_name}: {e}")
    else:
        st.warning("No audio files found in playlist.txt!")
    
    # Thêm thông tin hướng dẫn
    st.divider()
    st.info("💡 **Lưu ý:** Để xem thống kê và lịch sử sử dụng âm thanh, vui lòng truy cập trang **Statistics**.")

# Chạy giao diện
sound_controlUI()