#include <Adafruit_VC0706.h>
#include <SoftwareSerial.h>


SoftwareSerial cameraconnection = SoftwareSerial(4, 2);
Adafruit_VC0706 cam = Adafruit_VC0706(&cameraconnection);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("VC0706 Camera snapshot test");

  if (cam.begin()) {
    Serial.println("Camera Found:");
  } else {
    Serial.println("No camera found?");
    return;
  }
}

void loop() {
  
  // put your main code here, to run repeatedly:

}
