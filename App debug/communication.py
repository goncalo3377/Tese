import serial
import struct
import time
from PySide6.QtCore import QThread, Signal

class SerialManager(QThread):
    # Sinais para enviar dados limpos para a UI
    data_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, port='/dev/ttyACM0', baudrate=115200): 
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.ser = None

        # --- ESTRUTURA DE RECEÇÃO (Telemetria do ESP32) ---
        self.rx_format = "<H I ffff"
        self.rx_size = struct.calcsize(self.rx_format)
        self.expected_header = 0xBBAA 

        # --- ESTRUTURA DE ENVIO (Comandos para o ESP32) ---
        self.tx_format = "<H B ? ffffffffff"

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self.ser.flushInput()
            self.ser.flushOutput()
            
            print(f"Porta {self.port} aberta com sucesso. A aguardar dados...")
            
            while self.running:
                if self.ser.in_waiting >= self.rx_size:
                    header_bytes = self.ser.read(2)
                    if len(header_bytes) < 2:
                        continue
                    
                    header = struct.unpack("<H", header_bytes)[0]
                    
                    if header == self.expected_header:
                        payload = self.ser.read(self.rx_size - 2)
                        if len(payload) == (self.rx_size - 2):
                            ts, pos, vel, vq, vd = struct.unpack("<Iffff", payload)
                            
                            # =========================================================================
                            # MONITOREZAR DADOS: Adiciona este print para veres o fluxo no teu terminal
                            # =========================================================================
                            print(f"[ESP32 -> PC] TS: {ts:06d}ms | Pos: {pos:6.2f} rad | Vel: {vel:6.2f} rad/s | Vq: {vq:5.2f}V | Vd: {vd:5.2f}V")
                            
                            telemetria = {
                                "posicao": pos,
                                "velocidade": vel,
                                "tensao_q": vq,
                                "tensao_d": vd
                            }
                            self.data_received.emit(telemetria)
                    else:
                        # Se entrar muito aqui, significa que o Header não coincide (0xBBAA)
                        # Podes descomentar a linha abaixo se quiseres caçar erros de alinhamento:
                        # print(f"[ERRO ALINHAMENTO] Header lido: {hex(header)}")
                        self.ser.read(1)
                        
                self.msleep(2)
                
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()


                
    def send_cmd(self, modo_id, malhafechada, kp_pitch, ki_pitch, kd_pitch, lpf_pitch, kp_yaw, ki_yaw, kd_yaw, lpf_yaw, setpoint_pitch, setpoint_yaw):
        if self.ser and self.ser.is_open:
            try:
                cmd_header = 0xDDCC
                packet = struct.pack(self.tx_format, cmd_header, modo_id, malhafechada, kp_pitch, ki_pitch, kd_pitch, lpf_pitch, kp_yaw, ki_yaw, kd_yaw, lpf_yaw, setpoint_pitch, setpoint_yaw)
                self.ser.write(packet)
            except Exception as e:
                self.error_occurred.emit(f"Falha ao enviar comando: {e}")

    def stop(self):
        self.running = False
        self.wait()