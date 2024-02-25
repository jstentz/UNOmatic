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
  if (!AFMS.begin()) {         // create with the default frequency 1.6KHz
    Serial.println("Could not find Motor Shield. Check wiring.");
    while (1);
  }
  Serial.println("Motor Shield found.");
  stepperMotor->release();
  stepperMotor->setSpeed(70);
  dcMotor->setSpeed(255);
  dcMotor->run(RELEASE);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    String data = Serial.readStringUntil('\n');
    Serial.println(cmd);
    Serial.println(data);
    int value = data.toInt();
    if (cmd == 'd') { // deal
      servo.attach(10);  // attaches the servo on pin 10 to the servo object
      servo.write(0);
      delay(500);
      servo.write(90);
      servo.detach();
      dcMotor->run(FORWARD);
      delay(750);
      dcMotor->run(RELEASE);
    } else if (cmd == 'r') { // rotate 
      stepperMotor->step(value, FORWARD, DOUBLE);
      stepperMotor->release();
    }
    Serial.println("done");
  }
}
