#include "WiFi.h"
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <WiFiClient.h>
#include <PubSubClient.h> // Thêm thư viện MQTT
#include <esp_now.h>
#include <esp_wifi.h>
#include "HardwareSerial.h"
#include "DFRobotDFPlayerMini.h"

#define RX_PIN 20 //3 //20 vang
#define TX_PIN 21 //1 //21 xanh


// Thông tin Wi-Fi
const char* ssid = "Silverwing Lost";
const char* password = "10042005";
const uint8_t  peer_mac[6]= {0x78, 0x21, 0x84, 0xE4, 0xB1, 0x08};
const int CHANNEL = 0;

// Thông tin ntfy (HTTP)
const char* ntfy_server = "ntfy.sh";
const char* ntfy_topic = "ngu";
const int http_port = 80;

// Thông tin MQTT
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const char* mqtt_topic_schedule = "motion/notification/schedule";
const char* mqtt_topic_time_range = "motion/notification/time_range";
const char* mqtt_topic_status = "motion/notification/status";
const char* mqtt_topic_audio = "audio/play/nhom5";

// Cấu hình cảm biến PIR
#define sensorA 2
#define sensorB 3
int sensorA_value;
int sensorB_value;
int lastSensorA_value = LOW;
int lastSensorB_value = LOW;
bool sensorA_triggered = false;
unsigned long sensorA_triggerTime = 0;
const unsigned long triggerWindow = 10000;
unsigned long lastNotificationTime = 0;
const unsigned long notificationInterval = 30000;
bool first_time = true;
bool notificationsEnabled = true;
int notify_start_minutes = 0;
int notify_end_minutes = 0;

// Cấu hình NTP
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 7 * 3600);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

HardwareSerial myHardwareSerial(1);
DFRobotDFPlayerMini myDFPlayer; 

void setup() {
  Serial.begin(9600);
  pinMode(sensorA, INPUT);
  pinMode(sensorB, INPUT);

  myHardwareSerial.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(200);

  if (!myDFPlayer.begin(myHardwareSerial, true, true)) {
    Serial.println("Unable to begin:");
    Serial.println("1. Please recheck the connection!");
    Serial.println("2. Please insert the SD card!");
    while(true) {
      delay(1000);
    }
  }

  myDFPlayer.setTimeOut(500);
  myDFPlayer.volume(30);
  
  setup_wifi();
  timeClient.begin();

  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(mqttCallback);
  delay(1000);
  connectMQTT();
  esp_wifi_set_channel(CHANNEL, WIFI_SECOND_CHAN_NONE);
  delay(100);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  esp_now_peer_info_t peer = {};
  memcpy(peer.peer_addr, peer_mac, 6);
  peer.channel = CHANNEL;
  peer.encrypt = false;
  esp_now_add_peer(&peer);
}

void setup_wifi() {
  delay(10);
  Serial.println("Đang kết nối Wi-Fi...");
  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP("ESP_SENDER_AP", NULL, CHANNEL, false);
  WiFi.begin(ssid, password);
  int wifi_attempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifi_attempts < 20) {
    delay(500);
    Serial.print(".");
    wifi_attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Đã kết nối Wi-Fi!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Lỗi: Không thể kết nối Wi-Fi!");
    while (true);
  }
}

void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.println("Đang kết nối MQTT...");
    String clientId = "ESP32Client-" + String(random(0xffff), HEX);
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("Đã kết nối MQTT!");
      mqttClient.subscribe(mqtt_topic_schedule);
      mqttClient.publish(mqtt_topic_status, notificationsEnabled ? "ON" : "OFF");
      mqttClient.subscribe(mqtt_topic_time_range);
      mqttClient.subscribe(mqtt_topic_audio);
      Serial.println("Join ok");
    } else {
      Serial.print("Lỗi kết nối MQTT, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" Thử lại sau 5 giây...");
      delay(5000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.println("Topic nhận: " + String(topic));
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Nhận MQTT: " + String(topic) + " - " + message);
  
  if (String(topic) == mqtt_topic_time_range) {
    int sepIndex = message.indexOf('-');
    Serial.println("****************");
    Serial.println(message);
    Serial.println("***********");
    if (sepIndex != -1) {
      String startStr = message.substring(0, sepIndex);
      String endStr = message.substring(sepIndex + 1);
      
      int startHour = startStr.substring(0, 2).toInt();
      int startMin = startStr.substring(3, 5).toInt();
      int endHour = endStr.substring(0, 2).toInt();
      int endMin = endStr.substring(3, 5).toInt();

      notify_start_minutes = startHour * 60 + startMin;
      notify_end_minutes = endHour * 60 + endMin;

      Serial.print("Khung giờ chống trộm được cập nhật: ");
      Serial.print(startStr); Serial.print(" - "); Serial.println(endStr);
    }
  }
  if (String(topic) == mqtt_topic_audio) { 
    int fileNumber = message.toInt(); 
    if (fileNumber > 0) { 
      Serial.println("Playing file " + String(fileNumber)); 
      myDFPlayer.play(fileNumber); // Play the selected file 
    } 
    else { 
      Serial.println("Invalid file number!"); 
    } 
    Serial.println("Check audio");
  } 
}

bool isWithinNotificationTime(int nowMin, int startMin, int endMin) {
  if (startMin < endMin) {
    return nowMin >= startMin && nowMin < endMin;
  } else {
    return nowMin >= startMin || nowMin < endMin;
  }
}

void sendNtfyNotification(String message) {
  int nowMinutes = timeClient.getHours() * 60 + timeClient.getMinutes();
  notificationsEnabled = isWithinNotificationTime(nowMinutes, notify_start_minutes, notify_end_minutes);
  if (!notificationsEnabled) {
    Serial.println("Thông báo bị tắt, không gửi!");
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Mất kết nối Wi-Fi, đang thử lại...");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    int wifi_attempts = 0;
    while (WiFi.status() != WL_CONNECTED && wifi_attempts < 20) {
      delay(500);
      Serial.print(".");
      wifi_attempts++;
    }
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Lỗi: Không thể kết nối Wi-Fi!");
      return;
    }
    Serial.println("Đã kết nối lại Wi-Fi!");
  }

  if (wifiClient.connect(ntfy_server, http_port)) {
    Serial.println("Đang gửi thông báo...");
    String postData = message;
    String request = "POST /" + String(ntfy_topic) + " HTTP/1.1\r\n" +
                     "Host: " + String(ntfy_server) + "\r\n" +
                     "Content-Type: text/plain\r\n" +
                     "X-Title: Cảnh báo chuyển động\r\n" +
                     "X-Priority: high\r\n" +
                     "Content-Length: " + String(postData.length()) + "\r\n" +
                     "\r\n" +
                     postData;
    wifiClient.print(request);
    delay(500);
    while (wifiClient.available()) {
      String line = wifiClient.readStringUntil('\r');
      Serial.print(line);
    }
    Serial.println("Thông báo đã gửi!");
    Serial.println("------------------");
    Serial.println(notify_start_minutes);
    Serial.println(notify_end_minutes);
    Serial.println("------------------");
    wifiClient.stop();
  } else {
    Serial.println("Lỗi kết nối đến ntfy server!");
  }
}

bool detectMotion(
    int& sensorA_value,
    int& sensorB_value,
    int& lastSensorA_value,
    int& lastSensorB_value,
    bool& sensorA_triggered,
    unsigned long& sensorA_triggerTime,
    const unsigned long& triggerWindow,
    unsigned long& lastNotificationTime
) {
    unsigned long currentTime = millis();

    // Đọc giá trị cảm biến hiện tại
    sensorA_value = digitalRead(sensorA);
    sensorB_value = digitalRead(sensorB);

    // Kiểm tra xem cảm biến A vừa được kích hoạt
    if (sensorA_value == HIGH && lastSensorA_value == LOW) {
        sensorA_triggered = true;
        sensorA_triggerTime = currentTime;
    }

    // Nếu đã kích hoạt sensor A và sensor B cũng bật trong thời gian cho phép
    if (sensorA_triggered && sensorB_value == HIGH && lastSensorB_value == LOW) {
        if (currentTime - sensorA_triggerTime <= triggerWindow) {
            lastNotificationTime = currentTime;
            sensorA_triggered = false;
            return true;
        }
    }

    // Nếu quá thời gian cho phép thì reset trigger
    if (sensorA_triggered && currentTime - sensorA_triggerTime > triggerWindow) {
        sensorA_triggered = false;
        Serial.println("Hết cửa sổ 30 giây, đặt lại trạng thái PIR A");
    }

    // Cập nhật giá trị cuối của cảm biến
    lastSensorA_value = sensorA_value;
    lastSensorB_value = sensorB_value;

    return false;
}

const char msg[] = "EVENT";
bool first_time1 = true;

void loop() {
  if (first_time1) {
    unsigned long waitUntil = millis() + 12;
    while (millis() < waitUntil) {
      mqttClient.loop();
      delay(10);
    }
    first_time1 = false;
  }

  if (!mqttClient.connected()) { 
    connectMQTT(); 
  } 

  timeClient.update();
  mqttClient.loop();

  sensorA_value = digitalRead(sensorA);
  sensorB_value = digitalRead(sensorB);
  unsigned long currentTime = millis();

  Serial.print("PIR A: ");
  Serial.print(sensorA_value);
  Serial.print(" | PIR B: ");
  Serial.println(sensorB_value);

  if (detectMotion(sensorA_value, sensorB_value, lastSensorA_value, lastSensorB_value, sensorA_triggered, sensorA_triggerTime, triggerWindow, lastNotificationTime)) {
      if (esp_now_send(peer_mac, (uint8_t *) &msg, sizeof(msg)) != ESP_OK) {
        Serial.println("Send failed");
      }
      Serial.println("999999999999");
      String message = "Motion Detected: A then B at ";
      message += String(timeClient.getHours()) + ":" + String(timeClient.getMinutes()) + ":" + String(timeClient.getSeconds());
      message += ", 11/06/2025!";
      sendNtfyNotification(message);
      mqttClient.publish("motion/notification/event", message.c_str());
      Serial.println("Thông báo: " + message);
      lastNotificationTime = currentTime;
      sensorA_triggered = false;
      first_time = false;
  } 
  delay(100);
}
