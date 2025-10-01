// src/arm_controller.ino
#include <Servo.h>

// Servo pins (adjust as per your wiring)
Servo base, shoulder, elbow, wristPitch, wristRoll, gripper;

const int irPins[5] = {A0, A1, A2, A3, A4};
int sensorValues[5];
int baseSpeed = 150;
int Kp = 30;

// Motor pins (L298N)
#define L_ENA 5
#define L_IN1 6
#define L_IN2 7
#define R_ENA 9
#define R_IN1 10
#define R_IN2 11

void setup() {
  Serial.begin(115200);
  
  // Attach servos
  base.attach(2);
  shoulder.attach(3);
  elbow.attach(4);
  wristPitch.attach(8);
  wristRoll.attach(12);
  gripper.attach(13);

  // Motor pins
  pinMode(L_ENA, OUTPUT);
  pinMode(L_IN1, OUTPUT);
  pinMode(L_IN2, OUTPUT);
  pinMode(R_ENA, OUTPUT);
  pinMode(R_IN1, OUTPUT);
  pinMode(R_IN2, OUTPUT);

  goHome();
}

void goHome() {
  base.write(90);
  shoulder.write(90);
  elbow.write(90);
  wristPitch.write(90);
  wristRoll.write(90);
  gripper.write(0); // Open
  delay(1000);
}

void pickSequence() {
  // Lower arm
  shoulder.write(120);
  elbow.write(60);
  delay(800);
  // Close gripper
  gripper.write(65); // Close
  delay(500);
  // Lift
  shoulder.write(90);
  elbow.write(90);
  delay(800);
  // Rotate to bin
  base.write(160);
  delay(1000);
  // Release
  gripper.write(0);
  delay(500);
  // Return home
  base.write(90);
  delay(500);
}

int readLineError() {
  for (int i = 0; i < 5; i++) {
    sensorValues[i] = (analogRead(irPins[i]) > 750) ? 1 : 0;
  }
  // Weighted error: [-2,-1,0,1,2]
  int error = (-2 * sensorValues[0]) + (-1 * sensorValues[1]) + (0 * sensorValues[2]) +
              (1 * sensorValues[3]) + (2 * sensorValues[4]);
  return error;
}

void followLine() {
  int error = readLineError();
  int leftSpeed = baseSpeed + Kp * error;
  int rightSpeed = baseSpeed - Kp * error;

  leftSpeed = constrain(leftSpeed, 0, 255);
  rightSpeed = constrain(rightSpeed, 0, 255);

  // Left motor
  analogWrite(L_ENA, leftSpeed);
  digitalWrite(L_IN1, HIGH);
  digitalWrite(L_IN2, LOW);

  // Right motor
  analogWrite(R_ENA, rightSpeed);
  digitalWrite(R_IN1, HIGH);
  digitalWrite(R_IN2, LOW);
}

void loop() {
  // Line following always runs
  followLine();

  // Check for serial command
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "gotit") {
      // Stop AGV briefly
      analogWrite(L_ENA, 0);
      analogWrite(R_ENA, 0);
      delay(500);
      pickSequence();
      delay(1000);
    }
  }
}
