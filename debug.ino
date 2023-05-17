#include <LiquidCrystal.h>
#include <ESP8266WiFi.h>

void setup() {
  Serial.begin(9600);
  WiFi.begin("username", "password");
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("Disconnected");
  }

  Serial.println();
  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  float sensor_thermo_val;
  lcd.noDisplay();
  sensor_thermo_val = ((analogRead(analogPin)-32)/9) * 5;  
  delay(10000);
  Serial.println(sensor_thermo_val);
  if (sensor_thermo_val > = 37.5){ 
    lcd.print(val);
    lcd.display();
    Serial.println(val); 
  }
}
