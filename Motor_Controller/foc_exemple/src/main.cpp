#include <SimpleFOC.h>

BLDCMotor motor = BLDCMotor(7);
BLDCDriver3PWM driver = BLDCDriver3PWM(4, 5, 6, 7);

void setup(){
  driver.voltage_power_supply = 12.0;
  driver.voltage_limit = 12.0;
  driver.init();

  motor.linkDriver(&driver);

  motor.voltage_limit = 3;   // Tensão enviada para as fases
  motor.velocity_limit = 100; 
  motor.controller = MotionControlType::velocity_openloop;
  motor.init();
  motor.enable(); // Liga explicitamente
  delay(2000);
}

void loop(){
  motor.loopFOC();
  motor.move(1); 
}