#include <SimpleFOC.h>
#include <SimpleFOCDrivers.h>
#include <encoders/mt6835/MagneticSensorMT6835.h>
#include "comunicacao.h"
#include <deque> // Em vez de <vector

// 7 pares de polos, 8.85 Ohms, 225.53 KV
BLDCMotor motor_Pitch = BLDCMotor(7, 8.85, 225.53);
// 24N/22P,3Ω, ?
BLDCMotor motor_Yaw = BLDCMotor(11, 3);

// Pinos: PWM A, B, C e EN (Enable) no pino 7
BLDCDriver3PWM driver_Pitch = BLDCDriver3PWM(4, 5, 6, 7);
BLDCDriver3PWM driver_Yaw = BLDCDriver3PWM(15, 16, 17, 18);

MagneticSensorMT6835 sensor_Pitch = MagneticSensorMT6835(10);
MagneticSensorMT6835 sensor_Yaw = MagneticSensorMT6835(9);

volatile uint8_t atual_modo_id = 3; 
volatile float amplitude_Pitch = 0.0;
volatile float frequencia_Pitch = 0.0;
volatile float amplitude_Yaw = 0.0;
volatile float frequencia_Yaw = 0.0;

volatile float alvo_partilhado_Pitch = 0.0;
volatile float alvo_partilhado_Yaw = 0.0; 
volatile float alvo_instantaneo_Pitch = 0.0;
volatile float alvo_instantaneo_Yaw = 0.0;

volatile float setpoint_Pitch = 0.0; 
volatile float kd_Yaw = 0.0; 
volatile float lpf_encoder_pitch = 0.0; 

// --- MEMÓRIA DA BLACKBOX (Dinâmica e Espalhada) ---
struct LogData { 
    uint32_t ts; 
    float sp_p; float p_p; float v_p; float tensaoq_p; float tensaod_p;
    float sp_y; float p_y; float v_y; float tensaoq_y; float tensaod_y;
};
std::deque<LogData> log_buffer;
volatile uint8_t esp_estado_gravacao = 0; // 0=Idle, 1=Gravando, 2=Transmitindo

void comunicacao(void * pvParameters);
void aplicarParametros(ComandoRX parametros);

void setup() {
  Serial.begin(921600);
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
  //motor_Pitch.move(PI+setpoint_normalizado_Pitch);
  //motor_Yaw.move(PI+setpoint_normalizado_Yaw);

  float t = millis() / 1000.0; // Tempo em segundos

  // =========================================================================
  // GERADOR DE SINAIS INTERNO DO ESP32
  // =========================================================================
  if (atual_modo_id == 1) { 
      // MODO SENO: Multiplica a amplitude pelo seno do tempo e frequência
      alvo_instantaneo_Pitch = amplitude_Pitch * sin(2 * PI * frequencia_Pitch * t);
      alvo_instantaneo_Yaw = amplitude_Yaw * sin(2 * PI * frequencia_Yaw * t);
  } 
  else if (atual_modo_id == 2) { 
      // MODO QUADRADA
      float per_p = (frequencia_Pitch > 0) ? (1.0 / frequencia_Pitch) : 1.0;
      alvo_instantaneo_Pitch = (fmod(t, per_p) < (per_p / 2.0)) ? amplitude_Pitch : -amplitude_Pitch;
      
      float per_y = (frequencia_Yaw > 0) ? (1.0 / frequencia_Yaw) : 1.0;
      alvo_instantaneo_Yaw = (fmod(t, per_y) < (per_y / 2.0)) ? amplitude_Yaw : -amplitude_Yaw;
  } 
  else if (atual_modo_id == 3) { 
    alvo_instantaneo_Pitch = PI + remainder(alvo_partilhado_Pitch,2*PI);
    alvo_instantaneo_Yaw = PI + remainder(alvo_partilhado_Yaw,2*PI);
  }
  else {
      // MODOS FIXOS: Posição ou Velocidade normais
      alvo_instantaneo_Pitch = alvo_partilhado_Pitch;
      alvo_instantaneo_Yaw = alvo_partilhado_Yaw;
  }

  motor_Pitch.move(alvo_instantaneo_Pitch);
  motor_Yaw.move(alvo_instantaneo_Yaw);
  
}


void comunicacao(void * pvParameters) {
  
  // Configuração do "Metrónomo" do FreeRTOS para a Tarefa correr exatament a 100Hz (10ms)
  TickType_t xLastWakeTime;
  const TickType_t xFrequency = pdMS_TO_TICKS(10); 
  xLastWakeTime = xTaskGetTickCount();

  uint32_t delay_telemetria = 0;

  for (;;) {
    
    // 1. LER COMANDOS DO PC
    ComandoRX parametros = receberTelemetria();
    
    if (parametros.header == 0xDDCC) {
        aplicarParametros(parametros);
        
        //enviarEcho(parametros, alvo_instantaneo_Pitch, alvo_instantaneo_Yaw, motor_Yaw.shaft_angle);
        // MÁQUINA DE ESTADOS DA GRAVAÇÃO
        if (parametros.cmd_gravar == 1) {
            if (esp_estado_gravacao == 0) {
                log_buffer.clear(); 
                // Pré-aloca espaço para não fazer o ESP perder tempo a aumentar a memória a cada ponto
                esp_estado_gravacao = 1; 
            }
        } else if (parametros.cmd_gravar == 2) {
            esp_estado_gravacao = 2;
        } else {
            esp_estado_gravacao = 0; 
        }
    }

    // 2. SISTEMA DE GRAVAÇÃO NO VETOR (100x por segundo)
    if (esp_estado_gravacao == 1) {
        // Proteção: Só grava se o ESP32 ainda tiver mais de 30KB de RAM livre
        if (ESP.getFreeHeap() > 30000) {
            LogData current_data;
            current_data.ts = millis();
            current_data.sp_p = alvo_instantaneo_Pitch; current_data.p_p = motor_Pitch.shaft_angle; current_data.v_p = motor_Pitch.shaft_velocity;
            current_data.tensaoq_p = motor_Pitch.voltage.q;
            current_data.tensaod_p = motor_Pitch.voltage.d;
            current_data.sp_y = alvo_instantaneo_Yaw;   current_data.p_y = motor_Yaw.shaft_angle;   current_data.v_y = motor_Yaw.shaft_velocity;
            current_data.tensaoq_y = motor_Yaw.voltage.q;
            current_data.tensaod_y = motor_Yaw.voltage.d;
            
            log_buffer.push_back(current_data); // Insere no fim da lista dinâmica
        } else {
            // Se a memória encher (provavelmente após 1 minuto), auto-stop por segurança
            esp_estado_gravacao = 0; 
        }
    }

    // 3. ENVIAR TELEMETRIA NORMAL PARA GRÁFICOS EM TEMPO REAL
    if (esp_estado_gravacao != 2) {
        if (millis() - delay_telemetria > 33) {
            enviarTelemetriaCompleta(motor_Pitch.shaft_angle,
            motor_Pitch.shaft_velocity,
            motor_Pitch.voltage.q,
            motor_Pitch.voltage.d,
            alvo_instantaneo_Pitch,
            motor_Yaw.shaft_angle,   
            motor_Yaw.shaft_velocity,   
            motor_Yaw.voltage.q,   
            motor_Yaw.voltage.d,   
            alvo_instantaneo_Yaw);
        }
    }
    

    // 4. DESCARGA MACIÇA PARA O .CSV
    if (esp_estado_gravacao == 2) {
        for (size_t i = 0; i < log_buffer.size(); i++) {
            LogPacketTX lp;
            lp.timestamp_ms = log_buffer[i].ts;
            lp.setpoint_P = log_buffer[i].sp_p; 
            lp.posicao_P = log_buffer[i].p_p; 
            lp.velocidade_P = log_buffer[i].v_p;
            lp.tensao_q_P = log_buffer[i].tensaoq_p;
            lp.tensao_d_P = log_buffer[i].tensaod_p;
            lp.setpoint_Y = log_buffer[i].sp_y;
            lp.posicao_Y = log_buffer[i].p_y;
            lp.velocidade_Y = log_buffer[i].v_y;
            lp.tensao_q_Y = log_buffer[i].tensaoq_y;
            lp.tensao_d_Y = log_buffer[i].tensaod_y;

            Serial.write((uint8_t*)&lp, sizeof(lp));
            if (i % 10 == 0) vTaskDelay(pdMS_TO_TICKS(1)); 
        }

        // Avisar o PC que terminou
        LogPacketTX fim;
        fim.timestamp_ms = 0xFFFFFFFF; 
        Serial.write((uint8_t*)&fim, sizeof(fim));

        // Limpa o Vector
        log_buffer.clear();
        // ESTA LINHA É CRÍTICA: Obriga o C++ a devolver a memória à RAM do ESP32!
        log_buffer.shrink_to_fit(); 
        
        esp_estado_gravacao = 0; 
        comando.cmd_gravar = 0; 
    }

    // 5. METRÓNOMO DO RTOS: Adormece exatamente o tempo necessário para perfazer 10ms
    vTaskDelayUntil(&xLastWakeTime, xFrequency);
  }
}


void aplicarParametros(ComandoRX parametros){
    // 1. Atualizar os ganhos PID e Filtros normalmente
    atual_modo_id = parametros.modo_id;
    /*
    motor_Pitch.PID_velocity.P = parametros.kp_Pitch;
    motor_Pitch.PID_velocity.I = parametros.ki_Pitch;
    motor_Pitch.PID_velocity.D = parametros.kd_Pitch;
    motor_Pitch.LPF_angle = parametros.lpf_encoder_Pitch;

    motor_Yaw.PID_velocity.P = parametros.kp_Yaw;
    motor_Yaw.PID_velocity.I = parametros.ki_Yaw;
    motor_Yaw.PID_velocity.D = parametros.kd_Yaw;
    motor_Yaw.LPF_angle = parametros.lpf_encoder_Yaw;
    */
    // =========================================================================

    // 3. Mudar dinamicamente o tipo de controlo do SimpleFOC baseado no modo
    if (parametros.modo_id == 3) { 
        // MODO POSIÇÃO (ÂNGULO)
        motor_Pitch.controller = parametros.malhafechada ? MotionControlType::angle : MotionControlType::angle_openloop;
        motor_Yaw.controller = parametros.malhafechada ? MotionControlType::angle : MotionControlType::angle_openloop;
        alvo_partilhado_Pitch = parametros.setpoint_Pitch;
        alvo_partilhado_Yaw = parametros.setpoint_Yaw;
    } 
    else if (parametros.modo_id == 4) { 
        // MODO VELOCIDADE
        motor_Pitch.controller = parametros.malhafechada ? MotionControlType::velocity : MotionControlType::velocity_openloop;
        motor_Yaw.controller = parametros.malhafechada ? MotionControlType::velocity : MotionControlType::velocity_openloop;
        alvo_partilhado_Pitch = parametros.setpoint_Pitch;
        alvo_partilhado_Yaw = parametros.setpoint_Yaw;
    }
    else if (parametros.modo_id == 1 || parametros.modo_id == 2) {
        // MODOS ONDA (Seno / Quadrada) -> Atuação direta por Torque/Tensão
        motor_Pitch.controller = MotionControlType::torque;
        motor_Yaw.controller = MotionControlType::torque;
        amplitude_Pitch = parametros.setpoint_Pitch;
        amplitude_Yaw = parametros.setpoint_Yaw;
        frequencia_Pitch = parametros.frequencia_Pitch;
        frequencia_Yaw = parametros.frequencia_Yaw;
    }
    // 3. Atualizar os alvos com o valor que veio na mesma variável de setpoint
    alvo_partilhado_Pitch = parametros.setpoint_Pitch;
    alvo_partilhado_Yaw = parametros.setpoint_Yaw;
}