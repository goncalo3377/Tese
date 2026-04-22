#include <SimpleFOC.h>
#include <SimpleFOCDrivers.h>
#include <encoders/mt6835/MagneticSensorMT6835.h>

// 7 pares de polos, 8.85 Ohms, 225.53 KV
BLDCMotor motor = BLDCMotor(7, 8.85, 225.53);
// Pinos: PWM A, B, C e EN (Enable) no pino 7
BLDCDriver3PWM driver = BLDCDriver3PWM(4, 5, 6, 7);
MagneticSensorMT6835 sensor = MagneticSensorMT6835(10);

float posicao = 0; //rad
uint32_t t_ant = 0; // Alterado para uint32_t para evitar overflow rápido

void setup() {
  Serial.begin(115200);
  delay(1000);

  // 1. Inicializar Sensor
  sensor.init();
  motor.linkSensor(&sensor);

  // 2. Inicializar Driver
  driver.voltage_power_supply = 12.0;
  driver.voltage_limit = 10.0; // Limite de segurança
  driver.init();
  motor.linkDriver(&driver);

  // 3. Configuração do Motor
  motor.controller = MotionControlType::angle;
  motor.torque_controller = TorqueControlType::voltage;
  motor.voltage_limit = 9.0;   
  //motor.current_limit = 0.5; // Um pouco mais alto para o teste
  //motor.P_angle.P = 0.5;
  //motor.P_angle.I = 0.0;
  //motor.P_angle.D = 0.0;

  // Ativar monitorização para ver erros no Serial
  //motor.useMonitoring(Serial);
  //motor.monitor_variables = _MON_TARGET | _MON_VEL | _MON_ANGLE | _MON_VOLT_Q; 
  // 4. Inicializar Hardware do Motor
  motor.init();

  // 5. CALIBRAÇÃO (O passo que faltava!)
  // Este comando vai alinhar o sensor e o motor
  motor.initFOC();

  Serial.println("Motor pronto. A enviar comando de 0.5V...");
  delay(1000);
}

void loop() {
  // Executa o algoritmo FOC (essencial estar no loop)
  motor.loopFOC();

  // 3. Verifica se enviaste uma nova posição pelo Serial
  if (Serial.available() > 0) {
    posicao = Serial.parseFloat(); // Lê o número que escreveste
    
    // Limpa o buffer para evitar leituras erradas
    while(Serial.available() > 0) Serial.read(); 
    
    Serial.print("Novo alvo definido: ");
    Serial.println(posicao);
  }

  motor.move(posicao);
  //motor.monitor();


  if (millis() - t_ant > 100){
    t_ant = millis();
    Serial.print(">posicao:");
    Serial.println(motor.shaft_angle);
    Serial.print(">tensao:");
    Serial.println(motor.voltage.q);
  }
}

