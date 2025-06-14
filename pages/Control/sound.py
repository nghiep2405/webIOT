import streamlit as st
from mqttService import mqtt_client
from mqttService import MQTT_SONG_TOPIC

PLAYLIST_FILE = "playlist.txt"  # Place this file in the same directory as app.py or adjust path

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

def sound_controlUI():
    # Load and display audio files
    st.subheader("🔔 Chọn Bản Ghi Âm Để Phát")
    audio_files = load_playlist()
    if audio_files:
        cols = st.columns(2)  # Display 3 buttons per row, adjust as needed
        for idx, (file, display_name) in enumerate(audio_files, 1):
            with cols[(idx - 1) % 2]:
                if st.button(f"{display_name}", key=f"play_{idx}"):
                    try:
                        # Publish the file index to MQTT broker
                        mqtt_client.publish(MQTT_SONG_TOPIC, str(idx), qos=1)
                        st.success(f"Đang gửi lệnh phát {file}")  
                    except Exception as e:
                        st.error(f"Error sending play command for {file}: {e}")
    else:
        st.warning("No audio files found in playlist.txt!")

sound_controlUI()