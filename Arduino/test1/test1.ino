#include <VarSpeedServo.h>

VarSpeedServo servo0;

void setup() {
  // put your setup code here, to run once:
  servo0.attach(10);

  Serial.begin(9600);

  servo0.write(90);
  delay(500);

  
}

void loop() {
  // put your main code here, to run repeatedly:
  servo0.write(45);
  delay(2000);
  servo0.write(135);
  delay(2000);
}
