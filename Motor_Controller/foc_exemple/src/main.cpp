#include <SPI.h>
#include <Arduino.h>

const int CS_PIN = 10;

void setup() {
  Serial.begin(115200);
  pinMode(CS_PIN, OUTPUT);
  digitalWrite(CS_PIN, HIGH);
  SPI.begin();
}

void loop() {
  uint16_t address = 0x03; // Endereço inicial da posição
  uint8_t instruction = 0x30; // Comando de leitura '0011'

  SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE3));
  digitalWrite(CS_PIN, LOW);

  // Envia os 16 bits de cabeçalho (Instrução + Endereço)
  SPI.transfer(instruction); // instrução + 0x0(de endereço)
  SPI.transfer(address);     // endereço

  // Agora o sensor começa a enviar os dados (MISO)
  // Como queremos 21 bits, lemos 3 bytes seguidos (Burst Read)
  uint8_t b1 = SPI.transfer(0x00); // Angle [20:13]
  uint8_t b2 = SPI.transfer(0x00); // Angle [12:5]
  uint8_t b3 = SPI.transfer(0x00); // Angle [4:0] + Status

  digitalWrite(CS_PIN, HIGH);
  SPI.endTransaction();

  // Reconstrução dos 21 bits
  uint32_t angleRaw = ((uint32_t)b1 << 13) | ((uint32_t)b2 << 5) | (b3 >> 3);
  float graus = (angleRaw * 360.0) / 2097152.0;

  Serial.printf("Angulo: %.4f\n", graus);
  delay(50);
}