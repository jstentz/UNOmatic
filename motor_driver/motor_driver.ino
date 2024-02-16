void setup() {
  Serial.begin(9600);
}


void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    Serial.print("echo: ");
    Serial.println(data);
  }
  delay(100);
}
