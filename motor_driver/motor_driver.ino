#include <Servo.h>
#include <Adafruit_MotorShield.h>


Servo servo;  // create servo object to control a servo

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();

// Connect a stepper motor with 200 steps per revolution (1.8 degree)
// to motor port #2 (M3 and M4)
Adafruit_StepperMotor *stepperMotor = AFMS.getStepper(200, 2);

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *dcMotor = AFMS.getMotor(1);

int dealt;
int prev_dir;

void setup() {
  dealt = 0;
  Serial.begin(9600);
  if (!AFMS.begin()) {  // create with the default frequency 1.6KHz
    Serial.println("Could not find Motor Shield. Check wiring.");
    while (1)
      ;
  }
  stepperMotor->release();
  stepperMotor->setSpeed(60);
  dcMotor->run(RELEASE);
  dcMotor->setSpeed(255);
  pinMode(2, INPUT);
  attachInterrupt(digitalPinToInterrupt(2), ir_sensor, RISING);
  prev_dir = -1;
}

void ir_sensor() {
  dealt = 1;
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    String data = Serial.readStringUntil('\n');
    int value = data.toInt();
    if (cmd == 'd') {   // deal
        servo.attach(9);  // attaches the servo on pin 9 to the servo object
        servo.write(0);
        delay(700);
        servo.write(90);
        servo.detach();

        dcMotor->run(FORWARD);
        delay(700);
        dcMotor->run(RELEASE);
        delay(300);
        // servo.attach(9);
        // for (int i = 0; i < 2; i++) {
        //   servo.write(0);
        //   delay(150);
        //   servo.write(180);
        //   delay(150);
        // }
    } else if (cmd == 'u') {
        servo.attach(9);  // attaches the servo on pin 9 to the servo object
        servo.write(180);
        delay(500);
        servo.detach();
    } else if (cmd == 'r') {  // rotate
      uint8_t steps, dir;
      if (prev_dir == -1 || value == prev_dir) {
        steps = 198;
      } else {
        steps = 212;
      }
      if (value == 1) {
        dir = FORWARD;
      } else {
        dir = BACKWARD;
      }
      prev_dir = value;
      stepperMotor->step(steps, dir, DOUBLE);
      stepperMotor->release();
    }
    if (dealt) {
      Serial.println("t");
    } else {
      Serial.println("f");
    }
    dealt = 0;
  }
}
