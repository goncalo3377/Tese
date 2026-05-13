#include <SimpleFOC.h>
#include <SimpleFOCDrivers.h>
#include <encoders/mt6835/MagneticSensorMT6835.h>

// 7 pares de polos, 8.85 Ohms, 225.53 KV
BLDCMotor motor_Pitch = BLDCMotor(7, 8.85, 225.53);
// Pinos: PWM A, B, C e EN (Enable) no pino 7
BLDCDriver3PWM driver_Pitch = BLDCDriver3PWM(4, 5, 6, 7);
MagneticSensorMT6835 sensor_Pitch = MagneticSensorMT6835(10);


void setup() {
  Serial.begin(115200);
  _delay(1000);

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
  motor_Pitch.move(0);
}
