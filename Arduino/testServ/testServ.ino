#include <ESP32Servo.h>


Servo myServo;

void setup() {
  // put your setup code here, to run once:
  myServo.attach(21);

  myServo.write(20);
  delay(2000);
  myServo.write(160);
}

void loop() {
  // put your main code here, to run repeatedly:

}
