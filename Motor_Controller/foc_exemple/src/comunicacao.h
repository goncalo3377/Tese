#include <Arduino.h>

// Força o compilador a não deixar espaços vazios (padding) entre variáveis
struct __attribute__((packed)) TelemetriaTX {
    uint16_t header = 0xBBAA;
    uint32_t timestamp_ms;
    float posicao;
    float velocidade;
    float tensao_q;
    float tensao_d;
};

struct __attribute__((packed)) ComandoRX {
    uint16_t header; // Deve vir como 0xDDCC
    uint8_t modo_id;
    float kp;
    float ki;
    float kd;
    float lpf_encoder;
    float setpoint;
};

// Exemplo de Envio do ESP32 para o PC a cada 20ms:
void enviarTelemetria(float posicao, float velocidade, float tensao_vq, float tensao_vd ) {
    TelemetriaTX pacote;
    pacote.timestamp_ms = millis();
    pacote.posicao = posicao; 
    pacote.velocidade = velocidade;
    pacote.tensao_q = tensao_vq;
    pacote.tensao_d = tensao_vd;
    
    Serial.write((uint8_t*)&pacote, sizeof(pacote));
}

// Exemplo de Receção no ESP32 dentro do loop():
ComandoRX lerTelemetria() {
    if (Serial.available() >= sizeof(ComandoRX)) {
        ComandoRX comando;
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
}