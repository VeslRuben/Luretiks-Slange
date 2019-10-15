#include <VarSpeedServo.h>
#include <math.h>

int numberOfServos = 7;

VarSpeedServo myServo[7];

int A = 40;
float forwardPhi = (120.0 / 180.0) * M_PI;
float lateralPhi = (120.0 / 180.0) * M_PI;
int T = 1000;
int servSpeed = 0;


void setup() {
  Serial.begin(9600);

  for(int i = 0; i < 8; i++) {
    myServo[i].attach(i);
    myServo[i].write(90);
  }

}

void loop() {
  // put your main code here, to run repeatedly:
  goForward();
}

void goForward() {
  for(int i = 0; i < 4; i++) {
    myServo[i * 2].write(90 + updateAngle(T, i * forwardPhi, A), servSpeed);
  }
}

void goBackward() {
  for(int i = 0; i < 4; i++) {
    myServo[i * 2].write(90 + updateAngle(T, -i * forwardPhi, A), servSpeed);
  }
}

int updateAngle(float T, float phase, float A) {
  float y = A * sin(((2*M_PI) / T) * millis() + phase);
  return y;
}
