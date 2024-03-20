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

void setup() {
  Serial.begin(9600);
  if (!AFMS.begin()) {  // create with the default frequency 1.6KHz
    Serial.println("Could not find Motor Shield. Check wiring.");
    while (1)
      ;
  }
  stepperMotor->release();
  stepperMotor->setSpeed(70);
  dcMotor->run(RELEASE);
  dcMotor->setSpeed(255);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    String data = Serial.readStringUntil('\n');
    int value = data.toInt();
    if (cmd == 'd') {   // deal
      for (int i = 0; i < value; i++) {
        servo.attach(9);  // attaches the servo on pin 10 to the servo object
        servo.write(0);
        delay(750);
        servo.write(90);
        servo.detach();

        dcMotor->run(FORWARD);
        delay(600);
        dcMotor->run(RELEASE);

        // servo.attach(9);
        // for (int i = 0; i < 2; i++) {
        //   servo.write(0);
        //   delay(150);
        //   servo.write(180);
        //   delay(150);
        // }
        // servo.write(180);
        // delay(200);
        // servo.write(90);
        // servo.detach();
      }
    } else if (cmd == 'r') {  // rotate
      stepperMotor->step(value, FORWARD, DOUBLE);
      stepperMotor->release();
    }
    Serial.println("done");
  }
}
