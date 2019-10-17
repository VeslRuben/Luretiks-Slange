#include <WiFi.h>


const char* ssid = "MSI";
const char* password =  "12345678";

const uint16_t port = 6969;
const char * host = "192.168.137.1";

int jallaball[100][200];

boolean notSent = false;

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

  for (int i = 0; i < 100; i++) {
    for (int j = 0; j < 200; j++) {
      jallaball[i][j] = 1;
    }
  }

}

void loop()
{
  WiFiClient client;
  WiFiUDP udpClient;

  if (udpClient.begin(9696)) {
    if (!notSent) {
      udpClient.beginPacket(host, port);
      udpClient.write('a');
      udpClient.endPacket();
      udpClient.beginPacket(host,port);
      int numRows = sizeof(jallaball) / sizeof(jallaball[0]);
      int numCols = sizeof(jallaball[0]) / sizeof(jallaball[0][0]);
      udpClient.write(char(numRows));
      udpClient.write(' ');
      udpClient.write(char(numCols));
      udpClient.endPacket();
      delay(50);
      udpClient.beginPacket(host, port);
      for (int i = 0; i < numRows; i++) {
        for (int j = 0; j < numCols; j++) {
          udpClient.write(jallaball[i][j]);
        }
      }
      udpClient.endPacket();
      udpClient.beginPacket(host, port);
      udpClient.write('f');
      udpClient.endPacket();
      notSent = true;
      Serial.println("Finished sending");
    }
  } else {
    Serial.println("Connection failed");
  }



  //  if (!client.connect(host, port)) {
  //
  //    Serial.println("Connection to host failed");
  //
  //    delay(1000);
  //    return;
  //  }
  //
  //  Serial.println("Connected to server successful!");
  //
  //  while (client.connected()) {
  //    if (client.available()) {
  //      String y = client.readStringUntil('\n');
  //      if (y == "f") {
  //        Serial.println("Going forward");
  //        client.print("Going forward");
  //      } else if ( y == "b") {
  //        Serial.println("Going backward");
  //        client.print("Going backward");
  //      } else if (y == "v") {
  //        Serial.println("Adjusting left");
  //        client.print("Adjusting left");
  //      } else if (y == "h") {
  //        Serial.println("Adjusting right");
  //        client.print("Adjusting right");
  //      } else {
  //        Serial.println("Unkown command");
  //        client.print("array");
  //        client.print(sizeof(jallaball) / sizeof(jallaball[0]));
  //        client.print(sizeof(jallaball[0]) / sizeof(jallaball[0][0]));
  //      }
  //
  //    }
  //
  //    if (!notSent) {
  //      int numRows = sizeof(jallaball) / sizeof(jallaball[0]);
  //      int numCols = sizeof(jallaball[0]) / sizeof(jallaball[0][0]);
  //      client.println("array");
  //      client.println(numRows);
  //      client.println(numCols);
  //      for (int i = 0; i < numRows; i++) {
  //        for (int j = 0; j < numCols; j++) {
  //          client.print(jallaball[i][j]);
  //        }
  //      }
  //      client.println("fin");
  //      notSent = true;
  //      Serial.println("Finished sending");
  //    }

  delay(500);
}
