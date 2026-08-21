# Smart IoT Store Management Platform

A smart IoT store management system integrating ESP32 microcontrollers, live camera streaming, dual-sensor motion tracking, AI-powered customer demographic analytics, MQTT hardware control, and a unified web dashboard.

---

## 🌟 Key Features

- **Live Video Streaming**: Real-time MJPEG video feed from ESP32-CAM.
- **Customer Traffic Tracking**: Dual PIR sensor detection sequence (A → B) to detect store entry and log visitor timestamps.
- **AI Demographic Analytics**: Face extraction and age-group classification (`Children`, `Teen`, `Adult`, `Elderly`) using DeepFace and PyTorch ResNet-50.
- **Interactive Control Panel**:
  - **LED / Light Control**: Adjust ESP32-CAM flashlight brightness via HTTP slider.
  - **Audio Broadcast**: Trigger pre-configured store audio announcements via MQTT and DFPlayer Mini.
  - **Anti-Theft Scheduling**: Configure active security time windows with instant `ntfy.sh` mobile push alerts upon unauthorized motion.
- **Statistics & History Dashboard**: Altair-powered charts for daily customer traffic, age demographics, and detailed audio playback logs.
- **Authentication & Support**: Username/password and Google OAuth login, plus an integrated customer support chatbot.

---

## 🛠️ System Architecture & Tech Stack

```
[ ESP32-CAM ] ── (HTTP MJPEG Stream) ──► [ Streamlit Dashboard ]
[ ESP32-C3 ]  ── (MQTT / ESP-NOW)    ──► [ MQTT Broker ] ◄──► [ Streamlit / FastAPI ]
[ FastAPI ]   ── (Firestore Admin)   ──► [ Firebase Firestore Cloud DB ]
[ AI Pipeline]── (DeepFace + ResNet) ──► [ Age Group Classification ]
```

- **Frontend**: Streamlit, Altair, Pandas
- **Backend**: FastAPI, Uvicorn, Pydantic
- **Database**: Firebase Firestore
- **Communication Protocols**: MQTT (Paho-MQTT), HTTP, ESP-NOW, NTP, WebSockets
- **AI / Computer Vision**: PyTorch, torchvision, DeepFace, OpenCV, Pillow
- **Hardware**: ESP32-C3, ESP32-CAM, 2x PIR Motion Sensors, DFRobot DFPlayer Mini + Speaker, MicroSD card

---

## 📂 Project Structure

```
webIOT/
├── main.py                     # Streamlit entry point, auth routing & layout
├── tool.py                     # FastAPI REST API & Firestore interface
├── mqttService.py              # MQTT client configuration and connection
├── requirements.txt            # Python dependencies
├── playlist.txt                # Audio track mappings for DFPlayer Mini
├── pages/
│   ├── login_register/         # User login & registration pages
│   ├── live_cam/               # Live camera feed & real-time entry stream
│   ├── Control/                # Hardware controls (LED, Sound, Security)
│   ├── statistic/              # Analytics charts & audio logs
│   ├── chatbot/                # Support chatbot dialog
│   └── overview/               # Project & team information
├── models/
│   ├── model.py                # AI model inference & customer classification
│   ├── cam.py                  # Face extraction and testing script
│   └── model.pth               # Pre-trained ResNet-50 weights
├── esp32_c3/
│   └── esp32_c3.ino            # ESP32-C3 firmware (PIR, DFPlayer, MQTT, ntfy)
└── esp32_cam/
    ├── esp32_cam.ino           # ESP32-CAM firmware (Camera server & LED control)
    ├── app_httpd.cpp           # Camera HTTP handlers
    ├── camera_pins.h           # Pin configurations
    └── board_config.h          # Board definitions
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- Arduino IDE (with ESP32 board package installed)
- MQTT Broker (e.g., Mosquitto, EMQX, or HiveMQ)
- Firebase Project with Firestore enabled

### 2. Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nghiep2405/webIOT.git
   cd webIOT
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Firebase Credentials:**
   Place your Firebase service account key JSON file in the root directory (matching the filename in `tool.py`, e.g. `testh-4386a-firebase-adminsdk-*.json`).

4. **Update Network & Hardware Configurations:**
   - **MQTT Broker IP**: Update `MQTT_BROKER` in `mqttService.py` and `mqtt_server` in `esp32_c3/esp32_c3.ino`.
   - **ESP32-CAM IP**: Update `ESP32_STREAM_URL` in `pages/live_cam/live_cam.py` and `esp32_ip` in `pages/Control/led_control.py`.
   - **Wi-Fi Credentials**: Update `ssid` and `password` in `esp32_c3/esp32_c3.ino` and `esp32_cam/esp32_cam.ino`.

### 3. Flash Hardware Firmware
- Open `esp32_c3/esp32_c3.ino` in Arduino IDE, select ESP32-C3 board, and flash.
- Open `esp32_cam/esp32_cam.ino` in Arduino IDE, select AI Thinker ESP32-CAM, and flash.

### 4. Run the Application

Start the FastAPI backend server:
```bash
uvicorn tool:app --reload --port 8000
```

In a separate terminal, launch the Streamlit frontend dashboard:
```bash
streamlit run main.py
```

Open your browser at `http://localhost:8501`.

---

## 👥 Contributors

**Group 5 Project Team:**
- Nguyễn Anh Khoa
- Nguyễn An Nghiệp
- Trần Hoài Thiện Nhân

**Advisors:**
- Bùi Thanh Lâm
- Cao Xuân Nam
- Đặng Hoài Thương
