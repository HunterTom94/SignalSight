#include <Arduino.h>

const int sineWavePoints = 360;  // Resolution of the sine wave
const int sineWaveHz = 2;        // Frequency of the sine wave
float sineWave[sineWavePoints];

void setup() {
  // Initialize Serial
  Serial.begin(2000000);

  // Pre-calculate sine wave values
  for (int i = 0; i < sineWavePoints; i++) {
    sineWave[i] = sin(2 * PI * i / sineWavePoints);
  }
}

void loop() {
  // Send sine wave values at 2 Hz
  for (int i = 0; i < sineWavePoints; i++) {
    float value = sineWave[i];
    Serial.write((byte*)&value, sizeof(value)); // Send as binary
    // delay(1000 / sineWaveHz / sineWavePoints);  // Timing for 2 Hz frequency
    delayMicroseconds(1388);
  }
}
