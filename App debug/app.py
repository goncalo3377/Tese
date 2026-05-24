import sys
import csv
import time
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, Slot, Qt
from PySide6.QtUiTools import QUiLoader
import math

# Importamos o nosso gestor de comunicação recém-criado
from communication import SerialManager

app = QApplication(sys.argv)

loader = QUiLoader()
loader.registerCustomWidget(PlotWidget)

file = QFile('./App debug/debug.ui')
file.open(QFile.ReadOnly)
window = loader.load(file)
file.close()

window.doubleSpinBox_pos_veloc_Pitch.setMinimum(-100.0)
window.doubleSpinBox_pos_veloc_Yaw.setMinimum(-100.0)

# Legendas dos Gráficos
window.widget_posicao.setLabel('left', 'Posição Ângulo', units='rad')
window.widget_posicao.setLabel('bottom', 'Amostras')
window.widget_velocidade.setLabel('left', 'Velocidade Angular', units='rad/s')
window.widget_velocidade.setLabel('bottom', 'Amostras')

# --- CONFIGURAÇÃO DOS DADOS E GRÁFICOS ---
x_axis = list(range(100))
data_pos = [0] * 100
data_vel = [0] * 100

# NOVOS BUFFERS: Para guardar o histórico do sinal de referência (Setpoint)
data_pos_ref = [0] * 100
data_vel_ref = [0] * 100

is_recording = False      
recorded_data = []        
recording_start_time = 0  

modo_enviado = "Posição"
amp_enviada = 0.0
freq_enviada = 0.0
sp_pitch_enviado = 0.0
sp_yaw_enviado = 0.0

window.widget_posicao.setBackground('#262829')
curve_pos = window.widget_posicao.plot(x_axis, data_pos, pen=pg.mkPen('b', width=2))
# Nova linha tracejada azul para a referência de posição
curve_pos_ref = window.widget_posicao.plot(x_axis, data_pos_ref, pen=pg.mkPen('#00aaff', width=1.5, style=Qt.DashLine))
window.widget_velocidade.setBackground('#262829')
curve_vel = window.widget_velocidade.plot(x_axis, data_vel, pen=pg.mkPen('r', width=2))
# Nova linha tracejada vermelha/laranja para a referência de velocidade
curve_vel_ref = window.widget_velocidade.plot(x_axis, data_vel_ref, pen=pg.mkPen('#ffaa00', width=1.5, style=Qt.DashLine))

# --- FUNÇÃO DE ATUALIZAÇÃO DA UI (CHAMADA VIA SINAL SÉRIE) ---
@Slot(dict)
def update_ui_with_real_data(telemetria):
    global data_pos, data_vel, data_pos_ref, data_vel_ref, is_recording, recorded_data, recording_start_time
    global modo_enviado, amp_enviada, freq_enviada, sp_pitch_enviado, sp_yaw_enviado
    
    # 1. Atualizar buffers dos gráficos com dados REAIS vindos do ESP32
    data_pos = data_pos[1:] + [telemetria["posicao"]]
    data_vel = data_vel[1:] + [telemetria["velocidade"]]
    
    # 2. CALCULAR O SETPOINT TEÓRICO PARA O GRÁFICO
    modo = window.comboBox_setpoint.currentText()
    ref_pos = 0.0
    ref_vel = 0.0
    t_atual = time.time()

    if modo_enviado == "Seno":
        # Usa os valores estáveis que foram guardados no clique do botão
        ref_vel = amp_enviada * math.sin(2 * math.pi * freq_enviada * t_atual)
        ref_pos = 0.0 
        
    elif modo_enviado == "Quadrada":
        periodo = 1.0 / freq_enviada if freq_enviada > 0 else 1.0
        ref_vel = amp_enviada if (t_atual % periodo) < (periodo / 2) else -amp_enviada
        ref_pos = 0.0
        
    elif "Posição" in modo_enviado:
        ref_pos = sp_pitch_enviado
        ref_vel = 0.0 
        
    elif "Velocidade" in modo_enviado:
        ref_pos = 0.0
        ref_vel = sp_pitch_enviado

    # 3. Atualizar buffers das linhas de referência
    data_pos_ref = data_pos_ref[1:] + [ref_pos]
    data_vel_ref = data_vel_ref[1:] + [ref_vel]
    
    # 4. Atualizar todas as curvas no ecrã (Reais e Alvos)
    curve_pos.setData(x_axis, data_pos)
    curve_pos_ref.setData(x_axis, data_pos_ref)
    
    curve_vel.setData(x_axis, data_vel)
    curve_vel_ref.setData(x_axis, data_vel_ref)
    
    # 5. Atualizar as labels digitais
    if hasattr(window, 'label_Posicao'):
        window.label_Posicao.setText(f"{telemetria['posicao']:.2f}")
    if hasattr(window, 'label_Velocidade'):
        window.label_Velocidade.setText(f"{telemetria['velocidade']:.2f}")
    if hasattr(window, 'label_tensao_q'):
        window.label_tensao_q.setText(f"{telemetria['tensao_q']:.2f}")
    if hasattr(window, 'label_tensao_d'):
        window.label_tensao_d.setText(f"{telemetria['tensao_d']:.2f}")

    # 6. Gravação de logs
    if is_recording:
        timestamp_relativo = int((time.time() - recording_start_time) * 1000)
        recorded_data.append([timestamp_relativo, telemetria['posicao'], telemetria['velocidade']])

    #alterar_modo_sinal()


# --- ENVIAR PARÂMETROS PARA O ESP32 ---
def enviar_parametros_esp32():
    """Lê todos os valores configurados na interface e despacha-os via Serial"""
    # 1. Mapear qual o modo de setpoint_Pitch selecionado (convertido para ID numérico)
    global modo_enviado, amp_enviada, freq_enviada, sp_pitch_enviado, sp_yaw_enviado
    
    modo_texto = window.comboBox_setpoint.currentText()
    modo_enviado = modo_texto 
    
    amp_enviada = window.doubleSpinBox_amplitude_Pitch.value() if hasattr(window, 'doubleSpinBox_amplitude_Pitch') else 0.0
    freq_enviada = window.doubleSpinBox_frequencia_Pitch.value() if hasattr(window, 'doubleSpinBox_frequencia_Pitch') else 0.0

    modo_id = 0
    setpoint_Pitch = 0.0
    setpoint_Yaw = 0.0

    if modo_texto == "Seno":
        modo_id = 1
        setpoint_Pitch = amp_enviada 
    elif modo_texto == "Quadrada":
        modo_id = 2
        setpoint_Pitch = amp_enviada
    elif "Posição" in modo_texto:
        modo_id = 3
        setpoint_Pitch = window.doubleSpinBox_pos_veloc_Pitch.value() 
        setpoint_Yaw = window.doubleSpinBox_pos_veloc_Yaw.value()
    elif "Velocidade" in modo_texto:
        modo_id = 4
        setpoint_Pitch = window.doubleSpinBox_pos_veloc_Pitch.value() 
        setpoint_Yaw = window.doubleSpinBox_pos_veloc_Yaw.value()

    # Atualizamos as referências fixas enviadas
    sp_pitch_enviado = setpoint_Pitch
    sp_yaw_enviado = setpoint_Yaw

    # 2. Capturar os ganhos PID e Filtros das caixas de texto (Verifica os objectNames no teu Designer!)
    # Como tens Pitch e Yaw, podes escolher qual enviar ou ler o valor adequado. Exemplo para Pitch:
    kp_pitch = window.doubleSpinBox_Pitch_Kp.value() if hasattr(window, 'doubleSpinBox_Pitch_Kp') else 0.0
    ki_pitch = window.doubleSpinBox_Pitch_Ki.value() if hasattr(window, 'doubleSpinBox_Pitch_Ki') else 0.0
    kd_pitch = window.doubleSpinBox_Pitch_Kd.value() if hasattr(window, 'doubleSpinBox_Pitch_Kd') else 0.0
    kp_yaw = window.doubleSpinBox_Yaw_Kp.value() if hasattr(window, 'doubleSpinBox_Yaw_Kp') else 0.0
    ki_yaw = window.doubleSpinBox_Yaw_Ki.value() if hasattr(window, 'doubleSpinBox_Yaw_Ki') else 0.0
    kd_yaw = window.doubleSpinBox_Yaw_Kd.value() if hasattr(window, 'doubleSpinBox_Yaw_Kd') else 0.0
    
    # Filtro do Encoder LPF (Ajusta para a tua doubleSpinBox real do filtro)
    lpf_pitch = window.doubleSpinBox_lpf_pitch.value() if hasattr(window, 'doubleSpinBox_lpf_pitch') else 0.0
    lpf_yaw = window.doubleSpinBox_lpf_pitch.value() if hasattr(window, 'doubleSpinBox_lpf_pitch') else 0.0

    malhafechada = True
    # 3. Disparar o envio via thread binária
    serial_worker.send_cmd(modo_id, malhafechada, kp_pitch, ki_pitch, kd_pitch, lpf_pitch, kp_yaw, ki_yaw, kd_yaw, lpf_yaw, setpoint_Pitch, setpoint_Yaw)
    print(f"Comando enviado: Modo={modo_id}, PID=({kp_pitch},{ki_pitch},{kd_pitch}), LPF={lpf_pitch}, yaw Modo={modo_id}, PID=({kp_yaw},{ki_yaw},{kd_yaw}), LPF={lpf_yaw}, SP={setpoint_Pitch}")


# --- FUNÇÕES PARA CONTROLAR A GRAVAÇÃO ---
def toggle_recording():
    global is_recording, recorded_data, recording_start_time
    if not is_recording:
        recorded_data = [] 
        recording_start_time = time.time() 
        is_recording = True
        window.botao_dados.setText("Parar Gravação")
        window.botao_dados.setStyleSheet("background-color: #ff823a; font-weight: bold; color: white;")
        print("Gravação de dados iniciada...")
    else:
        is_recording = False
        window.botao_dados.setText("Gravar Dados")
        window.botao_dados.setStyleSheet("") 
        save_to_csv()

def save_to_csv():
    global recorded_data
    if not recorded_data: return
    filename = f"./App debug/ensaio_motor_{int(time.time())}.csv"
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp_ms', 'Posicao_rad', 'Velocidade_rads'])
            writer.writerows(recorded_data)
        print(f"Sucesso: Dados guardados em '{filename}'")
    except Exception as e:
        print(f"Erro ao guardar CSV: {e}")

def atualizar_lpf_pitch(valor_inteiro):
    # Converte de 0-10000 para 0.0000-1.0000 (4 casas decimais para alta precisão)
    valor_float = valor_inteiro / 100.0
    window.label_LPF_Pitch.setText(f"{valor_float:.2f}")

def atualizar_lpf_yaw(valor_inteiro):
    valor_float = valor_inteiro / 100.0
    window.label_LPF_Yaw.setText(f"{valor_float:.2f}")

def alterar_modo_sinal():
    modo = window.comboBox_setpoint.currentText()
    if "Posição" in modo:
        window.checkBox_loop.show()
        window.doubleSpinBox_pos_veloc_Pitch.show()
        if hasattr(window, 'lbl_posicao_velocidade_Pitch'): window.lbl_posicao_velocidade_Pitch.show()
        window.doubleSpinBox_pos_veloc_Yaw.show()
        if hasattr(window, 'lbl_posicao_velocidade_Yaw'): window.lbl_posicao_velocidade_Yaw.show()
        window.lbl_posicao_velocidade_Pitch.setText("Posição Pitch (rad)")
        window.lbl_posicao_velocidade_Yaw.setText("Posição Yaw (rad)")
        window.doubleSpinBox_frequencia_Pitch.hide()
        if hasattr(window, 'lbl_frequencia_Pitch'): window.lbl_frequencia_Pitch.hide()
        window.doubleSpinBox_amplitude_Pitch.hide()
        if hasattr(window, 'lbl_amplitude_Pitch'): window.lbl_amplitude_Pitch.hide()
        window.doubleSpinBox_frequencia_Yaw.hide()
        if hasattr(window, 'lbl_frequencia_Yaw'): window.lbl_frequencia_Yaw.hide()
        window.doubleSpinBox_amplitude_Yaw.hide()
        if hasattr(window, 'lbl_amplitude_Yaw'): window.lbl_amplitude_Yaw.hide()
    elif "Velocidade" in modo:
        window.checkBox_loop.show()
        window.doubleSpinBox_pos_veloc_Pitch.show()
        if hasattr(window, 'lbl_posicao_velocidade_Pitch'): window.lbl_posicao_velocidade_Pitch.show()
        window.doubleSpinBox_pos_veloc_Yaw.show()
        if hasattr(window, 'lbl_posicao_velocidade_Yaw'): window.lbl_posicao_velocidade_Yaw.show()
        window.lbl_posicao_velocidade_Pitch.setText("Velocidade Pitch (rad/s)")
        window.lbl_posicao_velocidade_Yaw.setText("Velocidade Yaw (rad/s)")
        window.doubleSpinBox_frequencia_Pitch.hide()
        if hasattr(window, 'lbl_frequencia_Pitch'): window.lbl_frequencia_Pitch.hide()
        window.doubleSpinBox_amplitude_Pitch.hide()
        if hasattr(window, 'lbl_amplitude_Pitch'): window.lbl_amplitude_Pitch.hide()
        window.doubleSpinBox_frequencia_Yaw.hide()
        if hasattr(window, 'lbl_frequencia_Yaw'): window.lbl_frequencia_Yaw.hide()
        window.doubleSpinBox_amplitude_Yaw.hide()
        if hasattr(window, 'lbl_amplitude_Yaw'): window.lbl_amplitude_Yaw.hide()
    else:
        window.checkBox_loop.hide()
        window.doubleSpinBox_pos_veloc_Pitch.hide()
        if hasattr(window, 'lbl_posicao_velocidade_Pitch'): window.lbl_posicao_velocidade_Pitch.hide()
        window.doubleSpinBox_pos_veloc_Yaw.hide()
        if hasattr(window, 'lbl_posicao_velocidade_Yaw'): window.lbl_posicao_velocidade_Yaw.hide()
        window.doubleSpinBox_frequencia_Pitch.show()
        if hasattr(window, 'lbl_frequencia_Pitch'): window.lbl_frequencia_Pitch.show()
        window.doubleSpinBox_amplitude_Pitch.show()
        if hasattr(window, 'lbl_amplitude_Pitch'): window.lbl_amplitude_Pitch.show()
        window.doubleSpinBox_frequencia_Yaw.show()
        if hasattr(window, 'lbl_frequencia_Yaw'): window.lbl_frequencia_Yaw.show()
        window.doubleSpinBox_amplitude_Yaw.show()
        if hasattr(window, 'lbl_amplitude_Yaw'): window.lbl_amplitude_Yaw.show()

def handle_serial_error(err_msg):
    print(f"ERRO SÉRIAL: {err_msg}")

# --- INICIALIZAÇÃO DA COMUNICAÇÃO SÉRIE ---
# Altera '/dev/ttyUSB0' para a tua porta real (ex: 'COM3' no Windows)
serial_worker = SerialManager(port='/dev/ttyACM0', baudrate=115200)
serial_worker.data_received.connect(update_ui_with_real_data)
serial_worker.error_occurred.connect(handle_serial_error)
serial_worker.start() # Inicializa a escuta em plano secundário

# CONEXÕES DE BOTÕES DA INTERFACE
window.botao_dados.clicked.connect(toggle_recording)
window.comboBox_setpoint.currentIndexChanged.connect(alterar_modo_sinal)

# Novas conexões para os filtros LPF atualizaram os labels dinamicamente
window.horizontalScrollBar_LPF_Pitch.valueChanged.connect(atualizar_lpf_pitch)
window.horizontalScrollBar_LPF_Yaw.valueChanged.connect(atualizar_lpf_yaw)

if hasattr(window, 'pushButton_enviar'):
    window.pushButton_enviar.clicked.connect(enviar_parametros_esp32)

alterar_modo_sinal()
window.show()
sys.exit(app.exec())