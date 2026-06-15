import serial
import struct
from PySide6.QtCore import QThread, Signal

class SerialManager(QThread):
    # Sinais para enviar dados limpos para a UI
    #data_received = Signal(dict)
    log_data_received = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, port='/dev/ttyACM0', baudrate=921600): 
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.ser = None
        self.rx_size = 46 # 2 header + 4 ts + 10 floats * 4 = 46 bytes
        # --- ESTRUTURA DE ENVIO (Comandos para o ESP32) ---
        self.tx_format = "<H B ? B B ffffffffffff"

        self.latest_telemetry = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self.ser.flushInput()
            self.ser.flushOutput()
            
            print(f"Porta {self.port} aberta com sucesso. A aguardar dados...")
            
            while self.running:
                while self.ser.in_waiting >= self.rx_size:
                    header_bytes = self.ser.read(2)
                    header = struct.unpack("<H", header_bytes)[0]
                    
                    if header == 0xBBAA: # PACOTE: TELEMETRIA GRÁFICOS
                        payload = self.ser.read(44)
                        d = struct.unpack("<Iffffffffff", payload)
                        self.latest_telemetry = {
                            "pitch": {"pos": d[1], "vel": d[2], "vq": d[3], "vd": d[4], "sp": d[5]},
                            "yaw":   {"pos": d[6], "vel": d[7], "vq": d[8], "vd": d[9], "sp": d[10]}
                        }
                        #self.data_received.emit(telemetria)

                    elif header == 0xCCAA: # PACOTE: DADOS BLACKBOX
                        payload = self.ser.read(self.rx_size - 2)
                        d = struct.unpack("<Iffffffffff", payload)
                        # Exporta: ts, sp_p, pos_p, vel_p, vq_p, vd_p, sp_y, pos_y, vel_y, vq_y, vd_y
                        self.log_data_received.emit([d[0], d[5], d[1], d[2], d[3], d[4], d[10], d[6], d[7], d[8], d[9]])
                    elif header == 0xEEAA: 
                        payload = self.ser.read(59) # 61 bytes - 2 bytes do header
                        # Máscara estendida com mais dois 'f' no final para as variáveis do move()
                        modo_id, malha, cmd_g, kpp, kip, kdp, lpfp, kpy, kiy, kdy, lpfy, spp, spy, freqp, freqy, movep, movey = struct.unpack("<B?Bffffffffffffff", payload)
                        
                        #print("\n" + "="*60)
                        #print(" [ESP32 Loopback] CONFIRMAÇÃO DE DADOS RECEBIDOS EM REAL-TIME")
                        #print(f" Modo ID: {modo_id} | Malha Fechada: {malha} | Estado Blackbox: {cmd_g}")
                        #print(f" Eixo Pitch -> PID: ({kpp:.2f}, {kip:.2f}, {kdp:.2f}) | LPF: {lpfp:.4f}")
                        #print(f" Eixo Yaw   -> PID: ({kpy:.2f}, {kiy:.2f}, {kdy:.2f}) | LPF: {lpfy:.4f}")
                        #print(f" Setpoint Nominal (PC) -> Pitch: {spp:.4f} | Yaw: {spy:.4f}")
                        print(f" Freq. Operação        -> Pitch: {freqp:.2f} Hz | Yaw: {freqy:.2f} Hz")
                        #print("-" * 60)
                        # EXIBIÇÃO NO TERMINAL DO VALOR QUE ENTROU EFETIVAMENTE NO .MOVE()
                        print(f" VALOR REAL NO .move() -> Pitch: {movep:.4f} | Yaw: {movey:.4f}")
                        print("="*60 + "\n")
                    else:
                        # Se entrar muito aqui, significa que o Header não coincide (0xBBAA)
                        # Podes descomentar a linha abaixo se quiseres caçar erros de alinhamento:
                        # print(f"[ERRO ALINHAMENTO] Header lido: {hex(header)}")
                        self.ser.read(1)
                        
                self.msleep(1)
                
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def get_latest_telemetry(self):
        return self.latest_telemetry

                
    def send_cmd(self, modo_id, malhafechada, cmd_gravar, sub_modo,kp_pitch, ki_pitch, kd_pitch, lpf_pitch, kp_yaw, ki_yaw, kd_yaw, lpf_yaw, setpoint_pitch, setpoint_yaw, freq_pitch, freq_yaw):
        if self.ser and self.ser.is_open:
            try:
                cmd_header = 0xDDCC
                packet = struct.pack(self.tx_format, cmd_header, modo_id, malhafechada, cmd_gravar, sub_modo, kp_pitch, ki_pitch, kd_pitch, lpf_pitch, kp_yaw, ki_yaw, kd_yaw, lpf_yaw, setpoint_pitch, setpoint_yaw, freq_pitch, freq_yaw)
                self.ser.write(packet)
            except Exception as e:
                self.error_occurred.emit(f"Falha ao enviar comando: {e}")

    def stop(self):
        self.running = False
        self.wait()