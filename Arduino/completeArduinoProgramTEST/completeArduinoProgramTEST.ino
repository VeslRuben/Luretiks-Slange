#include <Servo.h>
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

// Buffer for packetsize
byte packetBuffer[128];

// Establish the UDP-Client
WiFiUDP udpClient;

/////////////////////////////////////////////
// MOVEMENT VARIABLES
/////////////////////////////////////////////
// Number of servos
const int numberOfServos = 5;

//Homemade timer for movement in cycles
int movementTimer = 0;

// Establish servo array
Servo myServo[numberOfServos];

// Amplitude for the servos
int A = 30;

// Different phase shifts for the different movement
float forwardPhi = (120.0 / 180.0) * M_PI;
float lateralPhi = (100.0 / 180.0) * M_PI;
float rollingPhi = (90.0 / 180.0) * M_PI;
float rotatePhiV = (120.0 / 180.0) * M_PI;
float rotatePhiH = (50.0 / 180.0) * M_PI;

// Time constant
int T = 10000;

//Variable for speed of servos
int servSpeed = 0;

// DO NOT USE PINS 12-17, THESE MAKE PARSEPACKET CRASH THE WHOLE FUCKING SHIT
// SERVO LIBRARIES ARE FUCKING MORONIC
int servPins[5] = {4, 23, 22, 21, 25};

// Zero-point array for servos
int servZero[5] = {90, 93, 97, 87, 99};

// Booleans for movement
boolean goingForward = false;
boolean goingBackward = false;
boolean latLeft = false;
boolean latRight = false;
boolean rotCW = false;
boolean rotCCW = false;

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

  // Begin listening on port 9696
  udpClient.begin(9696);

  ////////////////////////////
  // MOVEMENT RELATED
  ///////////////////////////

  // Establishing the servos in an array
  for (int i = 0; i < 0 + numberOfServos; i++) {
    myServo[i].attach(servPins[i]);
    myServo[i].write(servZero[i]);
  }
}

void loop()
{
  //Checks for incoming packets
  char command = checkPackets();
  if (command != 'z') {
    
    // If packet is f, move forward
    if (command == 'f') {
      Serial.println("Going forward");
      goingForward = true;
      goingBackward = false;
      sendAliveMessage();
      
    // If packet is b, move backwards
    } else if (command == 'b') {
      Serial.println("Going backwards");
      goingForward = false;
      goingBackward = true;
      sendAliveMessage();

    // If packet is v, straighten out, lateral shift left
    } else if (command == 'v') {
      Serial.println("Adjusting left");
      sendAliveMessage();
      latLeft = true;
      latRight = false;
      //goStraight();

    // If packet is h, straighten out, lateral shift right
    } else if (command == 'h') {
      Serial.println("Adjusting right");
      sendAliveMessage();
      latRight = true;
      latLeft = false;
      //goStraight();

    // If packet is m, rotate CW
    } else if (command == 'm') {
      Serial.println("Rotating CW");
      sendAliveMessage();
      rotCW = true;
      rotCCW = false;
      //goStraight();

    // If packet is n, rotate CCW
    } else if (command == 'n') {
      Serial.println("Rotating CCW");
      sendAliveMessage();
      rotCCW = true;
      rotCW = false;
      //goStraight();

    // If packet is s, stop movement
    } else if (command == 's') {
      Serial.println("Stopping movement");
      goingForward = false;
      goingBackward = false;
      latRight = false;
      latLeft = false;
      sendAliveMessage();

    // If packet is r, adjust everything straight
    } else if (command == 'r') {
      Serial.println("Adjusting straight");
      sendAliveMessage();
      goingForward = false;
      goingBackward = false;
      latRight = false;
      latLeft = false;
      goStraight();
      sendDoneMessage();

    // If packet is t, change the turn-angle
    } else if (command == 't') {
      sendAliveMessage();
      int numb1 = (int)packetBuffer[1] - 48;
      int numb2 = (int)packetBuffer[2] - 48;
      int numb3 = (int)packetBuffer[3] -48;
      int sum = numb1 * 100 + numb2 * 10 + numb3;
      Serial.println(sum);
      turn(sum);
      sendDoneMessage();

    // If packet is p, change the T-parameter
    } else if (command == 'p') {
      int numb1 = (int)packetBuffer[1] - 48;
      int numb2 = (int)packetBuffer[2] - 48;
      int numb3 = (int)packetBuffer[3] - 48;
      int sum = numb1 * 100 + numb2 * 10 + numb3;
      sum = sum * 1000;
      T = sum;
      sendAliveMessage();

    // If packet is a, change the A-parameter
    } else if (command == 'a') {
       int numb1 = (int)packetBuffer[1] - 48;
       int numb2 = (int)packetBuffer[2] - 48;
       int sum = numb1 * 10 + numb2;
       if(sum > 80) {
        sum = 80;
       }
       A = sum;
      sendAliveMessage();

    // If packet is anything else, send error to UDP server
    } else {
      Serial.println("Unknown command");
      sendErrorToServer();
    }
  }

  // If boolean goingForward is high, go forward one cycle
  if (goingForward) {
    goForward();
    movementTimer++;
    if(movementTimer >= T) {
      goingForward = false;
      sendDoneMessage();
      movementTimer = 0;
    }

  // If boolean goingBackward is high, go backward one cycle
  } else if (goingBackward) {
    goBackward();
    movementTimer++;
    if(movementTimer >= T) {
      goingBackward = false;
      sendDoneMessage();
      movementTimer = 0;
    }
  // If boolean latLeft is high, lateral shifts left one cycle
  } else if (latLeft) {
    lateralLeft();
    movementTimer++;
    if(movementTimer >= T) {
      latLeft = false;
      //delay(10);
      //goStraight();
      sendDoneMessage();
      movementTimer = 0;
    }
  // If boolean latRight is high, lateral shifts right one cycle
  } else if (latRight) {
    lateralRight();
    movementTimer++;
    if(movementTimer >= T) {
      latRight = false;
      //delay(10);
      //goStraight();
      sendDoneMessage();
      movementTimer = 0;
    }
  // If boolean rotCW is high, rotates clockwise one cycle
  } else if (rotCW) {
    rotateCW();
    movementTimer++;
    if(movementTimer >= T) {
      rotCW = false;
      //delay(10);
      //goStraight();
      sendDoneMessage();
      movementTimer = 0;
    }
  // If boolean rotCCW is high, rotates counter-clockwise one cycle
  } else if (rotCCW) {
    rotateCCW();
    movementTimer++;
    if(movementTimer >= T) {
      rotCCW = false;
      //delay(10);
      //goStraight();
      sendDoneMessage();
      movementTimer = 0;
    }
  }
}



////////////////////////////////
// WIFI FUNCTIONS
////////////////////////////////

// Checks for incoming packets, stores in the buffer.
char checkPackets() {
  if (udpClient.parsePacket()) {
    Serial.println("Packet received");
    udpClient.read(packetBuffer, 128);
    Serial.println(char(packetBuffer[0]));
    return packetBuffer[0];
  } else {
    return 'z';
  }
}

// Sends error message to UDP-server
void sendErrorToServer() {
  udpClient.beginPacket(host, port);
  udpClient.write('x');
  udpClient.endPacket();
}

// Sends message that command is done to UDP server
void sendDoneMessage() {
  udpClient.beginPacket(host, port);
  udpClient.write('d');
  udpClient.endPacket();
}

// Sends acknowledge-message to UDP-server
void sendAliveMessage() {
  udpClient.beginPacket(host, port);
  udpClient.write('a');
  udpClient.endPacket();
}

///////////////////////////////////////////
// MOVEMENT FUNCTIONS
///////////////////////////////////////////
// Go forward
void goForward() {
  for (int i = 0; i < 3; i++) {
    myServo[i * 2].write(servZero[i * 2] + updateAngle(T, i * forwardPhi, A));
  }
}

// Go backward
void goBackward() {
  for (int i = 2; i >= 0; i--) {
    myServo[i * 2].write(servZero[i * 2] + updateAngle(T, -i * forwardPhi, A));
  }
}

/*
 * Sets the turn angle
 * param deg: the turn angle in degrees
 */
void turn(int deg) {
  if (deg < 45){
    deg = 45;
  } else if (deg > 135) {
    deg = 135;
  }
  for (int i = 0; i < 2; i++) {
    myServo[(i * 2) + 1].write(deg + servZero[(i * 2) + 1] - 90);
  }
}

/*
 * Lateral shifts left
 */
void lateralLeft() {
  for (int i = 0; i < 3; i++) {
    myServo[i * 2].write(servZero[i * 2] + updateAngle(T, -i * rotatePhiV, A));
    if (i < 2) {
      myServo[(i * 2) + 1].write(servZero[(i * 2) + 1] + updateAngle(T, -i * rotatePhiH, A));
    }
  }
}

/*
 * Lateral shifts right
 */
void lateralRight() {
  for (int i = 0; i < 3; i++) {
    myServo[i * 2].write(servZero[i * 2] + updateAngle(T, i * rotatePhiV, A));
    if (i < 2) {
      myServo[(i * 2) + 1].write(servZero[(i * 2) + 1] + updateAngle(T, i * rotatePhiH, A));
    }
  }
}

/*
 * Rotates Clockwise
 */
void rotateCW() {
  for (int i = 0; i < 3; i++) {
    myServo[i * 2].write(servZero[i * 2] + updateAngle(T, i * rotatePhiV, A));
    if (i == 0) {
      myServo[(i * 2) + 1].write(servZero[(i * 2) + 1] + updateAngle(T, i * rotatePhiH, A));
    } else if (i == 1) {
      myServo[(i * 2) + 1].write(servZero[(i * 2) + 1] + updateAngle(T, i * (rotatePhiH + M_PI), A));
    }
  }
}

/*
 * Rotates Counter-Clockwise
 */
void rotateCCW() {
  // Pass
  for (int i = 0; i < 3; i++) {
    myServo[i * 2].write(servZero[i * 2] + updateAngle(T, -i * rotatePhiV, A));
    if (i == 0) {
      myServo[(i * 2) + 1].write(servZero[(i * 2) + 1] + updateAngle(T, -i * rotatePhiH , A));
    } else if (i == 1) {
      myServo[(i * 2) + 1].write(servZero[(i * 2) + 1] + updateAngle(T, -i * (rotatePhiH + M_PI) , A));
    }
  }
}

/*
 * Sets every module straight
 */
void goStraight() {
  for (int i = 0; i < 5; i++) {
    myServo[i].write(servZero[i]);
  }
}

/*
 * Updates angle of servos
 * 
 * param T: period time for cycle
 * param phase: offset for angle
 * param A: amplitude of movement
 */
int updateAngle(float T, float phase, float A) {
  float y = A * sin(((2 * M_PI) / T) * movementTimer + phase);
  return y;
}
