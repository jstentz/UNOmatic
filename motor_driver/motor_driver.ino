#include <Wire.h>

void setup() {
  int addr = 0x8;
  Wire.begin(addr);
  Wire.onReceive(receiveEvent);

}

void receiveEvent(int howMany) {
  while (Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character
    digitalWrite(ledPin, c);
  }
}

void loop() {
  delay(1000);

}
