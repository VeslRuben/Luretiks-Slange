#include <VarSpeedServo.h>
#include <math.h>

const int numberOfServos = 5;

VarSpeedServo myServo[numberOfServos];

int A = 40;
float forwardPhi = (120.0 / 180.0) * M_PI;
float lateralPhi = (100.0 / 180.0) * M_PI;
float rollingPhi = (90.0 / 180.0) * M_PI;
float rotatePhiV = (120.0 / 180.0) * M_PI;
float rotatePhiH = (50.0 / 180.0) * M_PI;
int T = 1000;
int servSpeed = 0;


void setup() {
  Serial.begin(9600);

  for(int i = 10; i < 10 + numberOfServos; i++) {
    myServo[i].attach(i);
    myServo[i].write(90);
  }

}

void loop() {
  // put your main code here, to run repeatedly:
  goForward();
}

void goForward() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, i * forwardPhi, A), servSpeed);
  }
}

void goBackward() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, -i * forwardPhi, A), servSpeed);
  }
}

void turningGait(int turnAngle) {
  for(int i = 0; i < 3; i++) {
    myServo[(i*2)+1].write(90 + turnAngle, servSpeed);
  }
  for (int i = 0; i < 3; i++) {
    myServo[i*2].write(90 + updateAngle(T, i * forwardPhi, A), servSpeed);
  }
}

void lateralShift() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, i * lateralPhi, A), servSpeed);
    myServo[(i*2)+1].write(90 + updateAngle(T, i*lateralPhi, A), servSpeed);
  }
}

void doARoll() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, 0, A), servSpeed);
    myServo[(i*2)+1].write(90 + updateAngle(T, 90, A), servSpeed);
  }
}

void rotatingGait() {
  for(int i = 0; i < 3; i++) {
    myServo[i * 2].write(90 + updateAngle(T, i * rotatePhiV, A), servSpeed);
    myServo[(i*2)+1].write(90 + updateAngle(T, i*rotatePhiH, A), servSpeed);
  }
}

int updateAngle(float T, float phase, float A) {
  float y = A * sin(((2*M_PI) / T) * millis() + phase);
  return y;
}
