#include <ESP32Servo.h>
#include <WiFi.h>
#include <math.h>


//////////////////////////////////////////////
// WIFI VARIABLES 
/////////////////////////////////////////////
// Information for connecting to WiFi
const char* ssid = "MSI";
const char* password =  "12345678";

// Information for sending information via UDP
const uint16_t port = 6969;
const char * host = "192.168.137.1";

// Test array for sending
int jallaball[100][200];

// Flag for sending packet only once
boolean notSent = false;

// Buffer for packetsize
byte packetBuffer[100];

// Establish the UDP-Client
WiFiUDP udpClient;

/////////////////////////////////////////////
// MOVEMENT VARIABLES
/////////////////////////////////////////////

const int numberOfServos = 5;

// Establish servo array
Servo myServo[numberOfServos];

// Amplitude for the servos
int A = 40; 

// Different phase shifts for the different movement
float forwardPhi = (120.0 / 180.0) * M_PI;
float lateralPhi = (100.0 / 180.0) * M_PI;
float rollingPhi = (90.0 / 180.0) * M_PI;
float rotatePhiV = (120.0 / 180.0) * M_PI;
float rotatePhiH = (50.0 / 180.0) * M_PI;

// Time constant
int T = 1000;

//Variable for speed of servos
int servSpeed = 0;

/////////////////////////////////////////
// SETUP
/////////////////////////////////////////

void setup()
{
  Serial.begin(115200);

  ///////////////////////////
  // WIFI RELATED
  //////////////////////////

  // Starting wifi
  WiFi.begin(ssid, password);

  // Trying to connect to WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());

  // Making 2D array to send
  for (int i = 0; i < 100; i++) {
    for (int j = 0; j < 200; j++) {
      jallaball[i][j] = 1;
    }
  }

  // Begin listening on port 9696
  udpClient.begin(9696);

  ////////////////////////////
  // MOVEMENT RELATED
  ///////////////////////////
  
  // Establishing the servos in an array
  for(int i = 10; i < 10 + numberOfServos; i++) {
    myServo[i].attach(i);
    myServo[i].write(90);
  }
}

void loop()
{
 sendPacketOnce();
 checkPackets();
}



////////////////////////////////
// WIFI FUNCTIONS 
////////////////////////////////

void checkPackets() {
  if (udpClient.parsePacket()) {
    Serial.println("Packet received");
    udpClient.read(packetBuffer, 100);
    Serial.println(packetBuffer[0]);
  }
}

void sendPacketOnce() {
  if (!notSent) {
    udpClient.beginPacket(host, port);
    udpClient.write('a');
    udpClient.endPacket();
    udpClient.beginPacket(host, port);
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
}

///////////////////////////////////////////
// MOVEMENT FUNCTIONS
///////////////////////////////////////////
void goForward() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, i * forwardPhi, A));
  }
}

void goBackward() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, -i * forwardPhi, A));
  }
}

void turningGait(int turnAngle) {
  for(int i = 0; i < 3; i++) {
    myServo[(i*2)+1].write(90 + turnAngle);
  }
  for (int i = 0; i < 3; i++) {
    myServo[i*2].write(90 + updateAngle(T, i * forwardPhi, A));
  }
}

void lateralShift() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, i * lateralPhi, A));
    myServo[(i*2)+1].write(90 + updateAngle(T, i*lateralPhi, A));
  }
}

void doARoll() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, 0, A));
    myServo[(i*2)+1].write(90 + updateAngle(T, 90, A));
  }
}

void rotatingGait() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, i * rotatePhiV, A));
    myServo[(i*2)+1].write(90 + updateAngle(T, i*rotatePhiH, A));
  }
}

int updateAngle(float T, float phase, float A) {
  float y = A * sin(((2*M_PI) / T) * millis() + phase);
  return y;
}
