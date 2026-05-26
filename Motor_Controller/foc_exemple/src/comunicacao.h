#include <Arduino.h>

// Força o compilador a não deixar espaços vazios (padding) entre variáveis
struct __attribute__((packed)) TelemetriaTX {
    uint16_t header = 0xBBAA;
    uint32_t timestamp_ms;
    // Eixo Pitch
    float posicao_P;
    float velocidade_P;
    float tensao_q_P;
    float tensao_d_P;
    float setpoint_P;
    // Eixo Yaw
    float posicao_Y;
    float velocidade_Y;
    float tensao_q_Y;
    float tensao_d_Y;
    float setpoint_Y;
};

// --- ESTRUTURA PARA DESCARGA MACIÇA (BLACKBOX) ---
struct __attribute__((packed)) LogPacketTX {
    uint16_t header = 0xCCAA; // Header diferente!
    uint32_t timestamp_ms;
    // Eixo Pitch
    float posicao_P;
    float velocidade_P;
    float tensao_q_P;
    float tensao_d_P;
    float setpoint_P;
    // Eixo Yaw
    float posicao_Y;
    float velocidade_Y;
    float tensao_q_Y;
    float tensao_d_Y;
    float setpoint_Y;
};

struct __attribute__((packed)) ComandoRX {
    uint16_t header; // Deve vir como 0xDDCC
    uint8_t modo_id;
    bool malhafechada;
    uint8_t cmd_gravar; // NOVO: 0 = Idle, 1 = Gravar, 2 = Stop & Send
    float kp_Pitch;
    float ki_Pitch;
    float kd_Pitch;
    float lpf_encoder_Pitch;
    float kp_Yaw;
    float ki_Yaw;
    float kd_Yaw;
    float lpf_encoder_Yaw;
    float setpoint_Pitch;
    float setpoint_Yaw;
    float frequencia_Pitch;
    float frequencia_Yaw;
};


// --- NOVO: ESTRUTURA DE ECHO PARA VERIFICAÇÃO NO TERMINAL (53 bytes) ---
struct __attribute__((packed)) EchoPacketTX {
    uint16_t header = 0xEEAA; // Header exclusivo para o terminal
    uint8_t modo_id;
    bool malhafechada;
    uint8_t cmd_gravar;
    float kp_Pitch;
    float ki_Pitch;
    float kd_Pitch;
    float lpf_encoder_Pitch;
    float kp_Yaw;
    float ki_Yaw;
    float kd_Yaw;
    float lpf_encoder_Yaw;
    float setpoint_Pitch;
    float setpoint_Yaw;
    float frequencia_Pitch;
    float frequencia_Yaw;
    float move_Pitch;
    float move_Yaw;
};

// Função que envia de volta tudo o que o ESP32 leu na RAM
void enviarEcho(ComandoRX cmd, float move_P, float move_Y, float teste) {
    EchoPacketTX echo;
    echo.modo_id = cmd.modo_id;
    echo.malhafechada = cmd.malhafechada;
    echo.cmd_gravar = cmd.cmd_gravar;
    echo.kp_Pitch = cmd.kp_Pitch;
    echo.ki_Pitch = cmd.ki_Pitch;
    echo.kd_Pitch = cmd.kd_Pitch;
    echo.lpf_encoder_Pitch = cmd.lpf_encoder_Pitch;
    echo.kp_Yaw = cmd.kp_Yaw;
    echo.ki_Yaw = cmd.ki_Yaw;
    echo.kd_Yaw = cmd.kd_Yaw;
    echo.lpf_encoder_Yaw = cmd.lpf_encoder_Yaw;
    echo.setpoint_Pitch = cmd.setpoint_Pitch;
    echo.setpoint_Yaw = cmd.setpoint_Yaw;
    echo.frequencia_Pitch = cmd.frequencia_Pitch;
    echo.frequencia_Yaw = cmd.frequencia_Yaw;
    echo.move_Pitch = move_P;
    echo.move_Yaw = move_Y;
    
    Serial.write((uint8_t*)&echo, sizeof(echo));
}

ComandoRX comando;

// Exemplo de Envio do ESP32 para o PC a cada 20ms:
void enviarTelemetriaCompleta(float p_pos, float p_vel, float p_vq, float p_vd, float p_sp, float y_pos, float y_vel, float y_vq, float y_vd, float y_sp) {
    TelemetriaTX pacote;
    pacote.timestamp_ms = millis();
    pacote.posicao_P = p_pos; 
    pacote.velocidade_P = p_vel; 
    pacote.tensao_q_P = p_vq; 
    pacote.tensao_d_P = p_vd; 
    pacote.setpoint_P = p_sp;
    pacote.posicao_Y = y_pos; 
    pacote.velocidade_Y = y_vel; 
    pacote.tensao_q_Y = y_vq; 
    pacote.tensao_d_Y = y_vd; 
    pacote.setpoint_Y = y_sp;
    Serial.write((uint8_t*)&pacote, sizeof(pacote));
}


ComandoRX receberTelemetria() {
    if (Serial.available() >= sizeof(ComandoRX)) {
        // Espreita os primeiros dois bytes para ver se é o cabeçalho de comando correto
        uint16_t checkHeader;
        Serial.readBytes((char*)&checkHeader, 2);
        
        if (checkHeader == 0xDDCC) {
            comando.header = checkHeader;
            // Lê o resto dos bytes diretamente para a memória da struct temporária
            Serial.readBytes((char*)&comando + 2, sizeof(ComandoRX) - 2);
        } else {
            // Se o header estava corrompido, limpa 1 byte do buffer para tentar realinhar no próximo ciclo
            Serial.read();
        }
    }
    return comando;
}