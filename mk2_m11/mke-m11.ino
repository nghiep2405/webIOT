// #include "HardwareSerial.h"
// #include "DFRobotDFPlayerMini.h"

// #define RX_PIN 3 //16  //20
// #define TX_PIN 1 //0  //21 

// HardwareSerial myHardwareSerial(1); // UART1
// //HardwareSerial myHardwareSerial(2);

// DFRobotDFPlayerMini myDFPlayer;

// void setup()
// {
//   Serial.begin(9600);
//   delay(1000);  // cho Serial ổn định

//   myHardwareSerial.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
//   delay(200);

//   if (!myDFPlayer.begin(myHardwareSerial, true, true)) {
//     Serial.println("Unable to begin:");
//     Serial.println("1. Please recheck the connection!");
//     Serial.println("2. Please insert the SD card!");
//     while(true) {
//       delay(1000); // giữ chương trình đứng
//     }
//   }

//   myDFPlayer.setTimeOut(500);
//   myDFPlayer.volume(15);
// }

// void loop()
// {
//   myDFPlayer.play(1);
//   Serial.println("Play file 1");

//   delay(5000);  // chờ 20 giây

//   //myDFPlayer.stop();
//   Serial.println("Stop file 1");

//   delay(5000);

//   myDFPlayer.play(4);
//   Serial.println("Play file 4");
//   delay(5000);  // chờ 20 giây
// }

// Arduino Code for DFPlayer Mini with MQTT 
#include <WiFi.h> 
#include <PubSubClient.h> 
#include "HardwareSerial.h" 
#include "DFRobotDFPlayerMini.h"

#define RX_PIN 3 // RX pin for DFPlayer 
#define TX_PIN 1 // TX pin for DFPlayer

const char* ssid = "Bush05"; // Replace with your Wi-Fi SSID 
const char* password = "12345679"; // Replace with your Wi-Fi password

//const char* ssid = "Silerwing Lost"; // Replace with your Wi-Fi SSID 
//const char* password = "10042005"; // Replace with your Wi-Fi password

// const char* ssid = "KhoaNghiep"; // Replace with your Wi-Fi SSID 
// const char* password = "sotaiChinh?1:0"; // Replace with your Wi-Fi password

// MQTT configuration 
const char* mqtt_server = "broker.emqx.io"; // Public MQTT broker 
const int mqtt_port = 1883; 
const char* mqtt_topic = "audio/play"; // Topic to receive audio file commands

HardwareSerial myHardwareSerial(1); // UART1 for DFPlayer 
DFRobotDFPlayerMini myDFPlayer; 
WiFiClient wifiClient; 
PubSubClient mqttClient(wifiClient);

void setup_wifi() {
  delay(10); 
  Serial.println("Connecting to Wi-Fi..."); 
  WiFi.begin(ssid, password); 
  int wifi_attempts = 0; 
  while (WiFi.status() != WL_CONNECTED && wifi_attempts < 20) { 
    delay(500); Serial.print("."); 
    wifi_attempts++; 
  } 
  if (WiFi.status() == WL_CONNECTED) { 
    Serial.println("Wi-Fi connected!"); 
    Serial.print("IP: "); 
    Serial.println(WiFi.localIP()); 
  } 
  else { 
    Serial.println("Error: Wi-Fi connection failed!"); 
    while (true); // Halt if connection fails 
  } 
}

void connectMQTT() { 
  while (!mqttClient.connected()) { 
    Serial.println("Connecting to MQTT..."); 
    String clientId = "ArduinoClient-" + String(random(0xffff), HEX); 
    if (mqttClient.connect(clientId.c_str())) { 
      Serial.println("MQTT connected!"); 
      mqttClient.subscribe(mqtt_topic); // Subscribe to audio play topic 
    } 
    else { 
      Serial.print("MQTT connection failed, rc="); 
      Serial.print(mqttClient.state()); 
      Serial.println(" Retrying in 5 seconds..."); 
      delay(5000); 
    } 
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) { 
  String message; 
  for (unsigned int i = 0; i < length; i++) { 
    message += (char)payload[i]; 
  } 
  Serial.println("Received MQTT: " + String(topic) + " - " + message);

  if (String(topic) == mqtt_topic) { 
    int fileNumber = message.toInt(); 
    if (fileNumber > 0) { 
      Serial.println("Playing file " + String(fileNumber)); 
      myDFPlayer.play(fileNumber); // Play the selected file 
    } 
    else { 
      Serial.println("Invalid file number!"); 
    } 
  } 
}

void setup() { 
  Serial.begin(9600); 
  delay(1000); // Stabilize Serial

  myHardwareSerial.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN); delay(200);

  if (!myDFPlayer.begin(myHardwareSerial, true, true)) { 
    Serial.println("Unable to begin:"); 
    Serial.println("1. Please recheck the connection!"); 
    Serial.println("2. Please insert the SD card!"); 
    while(true) { 
      delay(1000); // Halt program 
    } 
  }

  myDFPlayer.setTimeOut(500); 
  myDFPlayer.volume(15); // Set volume (0-30)

  setup_wifi(); // Connect to Wi-Fi 
  mqttClient.setServer(mqtt_server, mqtt_port); 
  mqttClient.setCallback(mqttCallback); // Set MQTT callback 
  connectMQTT(); // Connect to MQTT 
}

void loop() { 
  if (!mqttClient.connected()) { 
    connectMQTT(); 
  } 
  mqttClient.loop(); // Process MQTT messages 
  delay(100); // Small delay to avoid overloading 
}
