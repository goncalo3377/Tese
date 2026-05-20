#include <SimpleFOC.h>
#include <SimpleFOCDrivers.h>
#include <encoders/mt6835/MagneticSensorMT6835.h>
#include "comunicacao.h"

// 7 pares de polos, 8.85 Ohms, 225.53 KV
BLDCMotor motor_Pitch = BLDCMotor(7, 8.85, 225.53);
// 24N/22P,3Ω, ?
BLDCMotor motor_Yaw = BLDCMotor(11, 3);

// Pinos: PWM A, B, C e EN (Enable) no pino 7
BLDCDriver3PWM driver_Pitch = BLDCDriver3PWM(4, 5, 6, 7);
BLDCDriver3PWM driver_Yaw = BLDCDriver3PWM(15, 16, 17, 18);

MagneticSensorMT6835 sensor_Pitch = MagneticSensorMT6835(10);
MagneticSensorMT6835 sensor_Yaw = MagneticSensorMT6835(9);

volatile float alvo_partilhado = 0.0; //rad

void comunicacao(void * pvParameters);

void setup() {
  Serial.begin(115200);
  _delay(1000);

  // --- colocar a função no núcleo 0 ---
  xTaskCreatePinnedToCore(
  comunicacao, // Função que será executada
  "Comunicacao", // Nome da tarefa
  10000, // Tamanho da pilha (stack)
  NULL, // Parâmetros de entrada
  1, // Prioridade
  NULL, // Handle da tarefa
  0 // NÚCLEO 0
  );

  //Driver
  //Pitch
  sensor_Pitch.init();
  motor_Pitch.linkSensor(&sensor_Pitch);
  //Yaw
  sensor_Yaw.init();
  motor_Yaw.linkSensor(&sensor_Yaw);

  //Driver
  //Pitch
  driver_Pitch.voltage_power_supply = 12.0;
  driver_Pitch.voltage_limit = 8.0; // Limite de segurança
  driver_Pitch.init();
  motor_Pitch.linkDriver(&driver_Pitch);
  //Yaw
  driver_Yaw.voltage_power_supply = 12.0;
  driver_Yaw.voltage_limit = 8.0; // Limite de segurança
  driver_Yaw.init();
  motor_Yaw.linkDriver(&driver_Yaw);

  //Motor
  //Pitch
  motor_Pitch.controller = MotionControlType::angle;
  motor_Pitch.torque_controller = TorqueControlType::voltage;
  motor_Pitch.voltage_limit = 4.0;
  motor_Pitch.velocity_limit = 20.0;
  motor_Pitch.init();
  motor_Pitch.initFOC();
  //Yaw
  motor_Yaw.controller = MotionControlType::angle;
  motor_Yaw.torque_controller = TorqueControlType::voltage;
  motor_Yaw.voltage_limit = 4.0;
  motor_Yaw.velocity_limit = 20.0;
  motor_Yaw.init();
  motor_Yaw.initFOC();

  delay(1000);
}

void loop() {
  motor_Pitch.loopFOC();
  motor_Yaw.loopFOC();
  float setpoint_normalizado = remainder(alvo_partilhado,2*PI);
  motor_Pitch.move(PI+setpoint_normalizado);
  motor_Yaw.move(PI+setpoint_normalizado);
}


// executado no outro núcleo
void comunicacao(void * pvParameters) {
String inputString = "";
inputString.reserve(10);

for (;;) { // Loop infinito da tarefa
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    if (inChar == '\n' || inChar == '\r') {
      if (inputString.length() > 0) {
        alvo_partilhado = inputString.toFloat();
        inputString = "";
      }
    } else if (isDigit(inChar) || inChar == '.' || inChar == '-') {
      inputString += inChar;
    }
  }

  
  //Serial.printf(">tensao_aplicada_Pitch:%.3f\n", motor_Pitch.voltage.q);
  //Serial.printf(">posicao_Yaw:%.4f\n", motor_Yaw.shaft_angle);
  //Serial.printf(">tensao_aplicada_Yaw:%.3f\n", motor_Yaw.voltage.q);
  enviarTelemetria(motor_Pitch.shaft_angle, motor_Pitch.shaft_velocity, motor_Pitch.voltage.q, motor_Pitch.voltage.d);
  //delay em ms
  vTaskDelay(pdMS_TO_TICKS(100));
}

}