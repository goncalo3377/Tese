#include <SimpleFOC.h>
#include <SimpleFOCDrivers.h>
#include <encoders/mt6835/MagneticSensorMT6835.h>

// 7 pares de polos, 8.85 Ohms, 225.53 KV
BLDCMotor motor_Pitch = BLDCMotor(7, 8.85, 225.53);
// Pinos: PWM A, B, C e EN (Enable) no pino 7
BLDCDriver3PWM driver_Pitch = BLDCDriver3PWM(4, 5, 6, 7);
MagneticSensorMT6835 sensor_Pitch = MagneticSensorMT6835(10);

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

  sensor_Pitch.init();
  motor_Pitch.linkSensor(&sensor_Pitch);

  driver_Pitch.voltage_power_supply = 12.0;
  driver_Pitch.voltage_limit = 8.0; // Limite de segurança
  driver_Pitch.init();
  motor_Pitch.linkDriver(&driver_Pitch);

  motor_Pitch.controller = MotionControlType::angle;
  motor_Pitch.torque_controller = TorqueControlType::voltage;
  motor_Pitch.voltage_limit = 4.0;
  motor_Pitch.velocity_limit = 40.0;
  //motor.P_angle.P = 20.0;
  motor_Pitch.motion_downsample = 1;
  motor_Pitch.init();
  motor_Pitch.initFOC();
}

void loop() {
  motor_Pitch.loopFOC();
  float setpoint_normalizado = remainder(alvo_partilhado,2*PI);
  motor_Pitch.move(setpoint_normalizado);
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

  Serial.printf(">posicao:%.4f\n", motor_Pitch.shaft_angle);
  Serial.printf(">tensao_aplicada:%.3f\n", motor_Pitch.voltage.q);
  Serial.printf(">move_time:%lu\n", motor_Pitch.move_time_us);
  Serial.printf(">loopfoc_loop:%lu\n", motor_Pitch.loopfoc_time_us);
  Serial.print("angulo: ");
  Serial.println(sensor_Pitch.getAngle());

  //delay em ms
  vTaskDelay(pdMS_TO_TICKS(100));
}

}