#include <ESP32Servo.h>


Servo myServo;

void setup() {
  // put your setup code here, to run once:
  myServo.attach(25);

  myServo.write(99);
}

void loop() {
  // put your main code here, to run repeatedly:

}
