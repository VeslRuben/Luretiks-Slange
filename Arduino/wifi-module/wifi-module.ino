#include <WiFi.h>
 
const char* ssid = "RD";
const char* password =  "11111111";
 
const uint16_t port = 6969;
const char * host = "192.168.43.120";
 
void setup()
{
 
  Serial.begin(115200);
 
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }
 
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
 
}
 
void loop()
{
    WiFiClient client;
 
    if (!client.connect(host, port)) {
 
        Serial.println("Connection to host failed");
 
        delay(1000);
        return;
    }
 
    Serial.println("Connected to server successful!");
 
    client.print("Hello from ESP32!");

    while(millis() < 10000) {
      byte y = client.read();
      if(y != -1) {
        Serial.println(y);
      }
    }
    Serial.println(client.read());
 
    Serial.println("Disconnecting...");

    
    client.stop();
 
    delay(10000);
}
