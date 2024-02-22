#include <Servo.h>
#include <Adafruit_MotorShield.h>


Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards
// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61);

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *myMotor = AFMS.getMotor(2);
// You can also make another motor on port M2
//Adafruit_DCMotor *myOtherMotor = AFMS.getMotor(2);

void setup() {
  Serial.begin(9600);
  // myservo.attach(10);  // attaches the servo on pin 10 to the servo object
    if (!AFMS.begin()) {         // create with the default frequency 1.6KHz
  // if (!AFMS.begin(1000)) {  // OR with a different frequency, say 1KHz
    Serial.println("Could not find Motor Shield. Check wiring.");
    while (1);
  }
  Serial.println("Motor Shield found.");
  myMotor->run(RELEASE);
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    Serial.println(data);
    int value = data.toInt();
    // myservo.write(value);
    myMotor->run(FORWARD);
    myMotor->setSpeed(value);
    delay(1000);
    myMotor->run(RELEASE);
  }
  delay(10);
}
