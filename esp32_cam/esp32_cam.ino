#include "esp_camera.h"
#include <WiFi.h>
#include <esp_wifi.h>
#include <HTTPClient.h>
#include <esp_now.h>
#include "board_config.h"
#include <WiFiManager.h>
// #include <PubSubClient.h> 
// #include "HardwareSerial.h" 
// #include "DFRobotDFPlayerMini.h"

// #define RX_PIN 3 // RX pin for DFPlayer 
// #define TX_PIN 1 // TX pin for DFPlayer

// // Wifi and server
// const char *ssid = "IPhone";
// const char *password = "nak050105";
const char *postServer = "http://172.20.10.2:8000/upload/";

// // MQTT configuration 
// const char* mqtt_server = "broker.emqx.io"; // Public MQTT broker 
// const int mqtt_port = 1883; 
// const char* mqtt_topic = "audio/play"; // Topic to receive audio file commands

// HardwareSerial myHardwareSerial(1); // UART1 for DFPlayer 
// DFRobotDFPlayerMini myDFPlayer; 
// WiFiClient wifiClient; 
// PubSubClient mqttClient(wifiClient);

void startCameraServer();
void setupLedFlash();

// Callback function
static volatile bool captureRequested = false;
void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  captureRequested = true;
}

void sendPhotoHTTP(camera_fb_t *fb) {
  HTTPClient http;
  http.begin(postServer);
  http.addHeader("Content-Type", "image/jpeg");

  int code = http.POST(fb->buf, fb->len);
  if (code <= 0) {
    Serial.printf("POST error %d: %s\n", code, http.errorToString(code).c_str());
  } else {
    Serial.printf("HTTP POST code: %d\n", code);
  }
  http.end();
}

// void setup_wifi() {
//   delay(10); 
//   Serial.println("Connecting to Wi-Fi..."); 
//   WiFi.begin(ssid, password); 
//   int wifi_attempts = 0; 
//   while (WiFi.status() != WL_CONNECTED && wifi_attempts < 20) { 
//     delay(500); Serial.print("."); 
//     wifi_attempts++; 
//   } 
//   if (WiFi.status() == WL_CONNECTED) { 
//     Serial.println("Wi-Fi connected!"); 
//     Serial.print("IP: "); 
//     Serial.println(WiFi.localIP()); 
//   } 
//   else { 
//     Serial.println("Error: Wi-Fi connection failed!"); 
//     while (true); // Halt if connection fails 
//   } 
// }

// void connectMQTT() { 
//   while (!mqttClient.connected()) { 
//     Serial.println("Connecting to MQTT..."); 
//     String clientId = "ArduinoClient-" + String(random(0xffff), HEX); 
//     if (mqttClient.connect(clientId.c_str())) { 
//       Serial.println("MQTT connected!"); 
//       mqttClient.subscribe(mqtt_topic); // Subscribe to audio play topic 
//     } 
//     else { 
//       Serial.print("MQTT connection failed, rc="); 
//       Serial.print(mqttClient.state()); 
//       Serial.println(" Retrying in 5 seconds..."); 
//       delay(5000); 
//     } 
//   }
// }

// void mqttCallback(char* topic, byte* payload, unsigned int length) { 
//   String message; 
//   for (unsigned int i = 0; i < length; i++) { 
//     message += (char)payload[i]; 
//   } 
//   Serial.println("Received MQTT: " + String(topic) + " - " + message);

//   if (String(topic) == mqtt_topic) { 
//     int fileNumber = message.toInt(); 
//     if (fileNumber > 0) { 
//       Serial.println("Playing file " + String(fileNumber)); 
//       myDFPlayer.play(fileNumber); // Play the selected file 
//     } 
//     else { 
//       Serial.println("Invalid file number!"); 
//     } 
//   } 
// }

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // myHardwareSerial.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN); delay(200);

  // if (!myDFPlayer.begin(myHardwareSerial, true, true)) { 
  //   Serial.println("Unable to begin:"); 
  //   Serial.println("1. Please recheck the connection!"); 
  //   Serial.println("2. Please insert the SD card!"); 
  //   while(true) { 
  //     delay(1000); // Halt program 
  //   } 
  // }

  // myDFPlayer.setTimeOut(500); 
  // myDFPlayer.volume(15); // Set volume (0-30)

  // //setup_wifi(); // Connect to Wi-Fi 
  // mqttClient.setServer(mqtt_server, mqtt_port); 
  // mqttClient.setCallback(mqttCallback); // Set MQTT callback 
  // connectMQTT(); // Connect to MQTT 

  // Accesspoint
  Serial.println("Connected wifiManager");
  WiFiManager wifiManager;
  wifiManager.resetSettings();
  if(!wifiManager.autoConnect("My Accesspoint")){
    Serial.println("Failed to connect and hit timeout");
    ESP.restart();
    delay(1000);
  }
  Serial.println("Connected wifi");

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG; // for streaming
  // config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      // Limit the frame size when PSRAM is not available
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);       // flip it back
    s->set_brightness(s, 2);  // up the brightness just a bit
    s->set_saturation(s, -2); // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA);
  }

// Setup LED FLash if LED pin is defined in camera_pins.h
#if defined(LED_GPIO_NUM)
  setupLedFlash();
#endif

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP_NOW failed");
  }

  esp_now_register_recv_cb(onDataRecv);
}

void loop() {
  // Do nothing. Everything is done in another task by the web server
  if (captureRequested) {
    Serial.println("Sent");
    captureRequested = false;
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }
    Serial.printf("Captured %u bytes\n", fb->len);
    sendPhotoHTTP(fb);
    esp_camera_fb_return(fb);
  }
  delay(10000);
}