import sys
import csv
import time
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, Slot, Qt
from PySide6.QtUiTools import QUiLoader
from communication import SerialManager

# --- INICIALIZAÇÃO DA APLICAÇÃO E INTERFACE ---
app = QApplication(sys.argv)
loader = QUiLoader()
loader.registerCustomWidget(PlotWidget)

file = QFile('./App debug/debug.ui')
file.open(QFile.ReadOnly)
window = loader.load(file)
file.close()

# Forçar limites negativos diretamente por software para os ensaios de inversão
window.doubleSpinBox_pos_veloc_Pitch.setMinimum(-100.0)
window.doubleSpinBox_pos_veloc_Yaw.setMinimum(-100.0)

# Configuração de limites e eixos dos 6 sub-gráficos da Estação
window.widget_posicao_Pitch.setLabel('left', 'Posição', units='rad')
window.widget_velocidade_Pitch.setLabel('left', 'Velocidade', units='rad/s')
window.widget_tensaoq_Pitch.setLabel('left', 'Tensão Q', units='V')
window.widget_posicao_Yaw.setLabel('left', 'Posição', units='rad')
window.widget_velocidade_Yaw.setLabel('left', 'Velocidade', units='rad/s')
window.widget_tensaoq_Yaw.setLabel('left', 'Tensão Q', units='V')

# --- CONFIGURAÇÃO DOS BUFFERS DE DADOS ---
n_amostras = 100
x_axis = list(range(n_amostras))
buffers = {
    "P": {"pos": [0]*n_amostras, "vel": [0]*n_amostras, "vq": [0]*n_amostras, "sp_pos": [0]*n_amostras, "sp_vel": [0]*n_amostras, "sp_vq": [0]*n_amostras},
    "Y": {"pos": [0]*n_amostras, "vel": [0]*n_amostras, "vq": [0]*n_amostras, "sp_pos": [0]*n_amostras, "sp_vel": [0]*n_amostras, "sp_vq": [0]*n_amostras}
}
# Variáveis globais de controlo de estado
is_recording = False      
recorded_data = []        
cmd_gravar_global = 0  # 0=Idle, 1=Start Recording, 2=Stop & Request Dump
modo_enviado = "Posição"

# --- DECLARAÇÃO DE CURVAS PYQTGRAPH ---
window.widget_posicao_Pitch.setBackground("#262829")
curve_p_pos = window.widget_posicao_Pitch.plot(pen='b', width=2)
curve_p_sp_pos = window.widget_posicao_Pitch.plot(pen=pg.mkPen('#00aaff', width=1.5, style=Qt.DashLine))

window.widget_velocidade_Pitch.setBackground('#262829')
curve_p_vel = window.widget_velocidade_Pitch.plot(pen='r', width=2)
curve_p_sp_vel = window.widget_velocidade_Pitch.plot(pen=pg.mkPen('#ffaa00', width=1.5, style=Qt.DashLine))

window.widget_tensaoq_Pitch.setBackground('#262829')
curve_p_vq = window.widget_tensaoq_Pitch.plot(pen='g', width=2)
curve_p_sp_vq = window.widget_tensaoq_Pitch.plot(pen=pg.mkPen('#00ffcc', width=1.5, style=Qt.DashLine))

window.widget_posicao_Yaw.setBackground('#262829')
curve_y_pos = window.widget_posicao_Yaw.plot(pen='b', width=2)
curve_y_sp_pos = window.widget_posicao_Yaw.plot(pen=pg.mkPen('#00aaff', width=1.5, style=Qt.DashLine))

window.widget_velocidade_Yaw.setBackground('#262829')
curve_y_vel = window.widget_velocidade_Yaw.plot(pen='r', width=2)
curve_y_sp_vel = window.widget_velocidade_Yaw.plot(pen=pg.mkPen('#ffaa00', width=1.5, style=Qt.DashLine))

window.widget_tensaoq_Yaw.setBackground('#262829')
curve_y_vq = window.widget_tensaoq_Yaw.plot(pen='g', width=2)
curve_y_sp_vq = window.widget_tensaoq_Yaw.plot(pen=pg.mkPen('#00ffcc', width=1.5, style=Qt.DashLine))

# --- REFEITORADO: ATUALIZAÇÃO FLUIDA DA INTERFACE (SINAL REAL-TIME) ---
@Slot(dict)
def update_ui_with_real_data(telemetria):
    global modo_enviado
    
    for k, eixo in [("pitch", "P"), ("yaw", "Y")]:
        t = telemetria[k]
        buffers[eixo]["pos"] = buffers[eixo]["pos"][1:] + [t["pos"]]
        buffers[eixo]["vel"] = buffers[eixo]["vel"][1:] + [t["vel"]]
        buffers[eixo]["vq"]  = buffers[eixo]["vq"][1:]  + [t["vq"]]
        
        # Alinhamento automático do setpoint conforme a grandeza física sob teste
        buffers[eixo]["sp_pos"] = buffers[eixo]["sp_pos"][1:] + [t["sp"] if "Posição" in modo_enviado else 0.0]
        buffers[eixo]["sp_vel"] = buffers[eixo]["sp_vel"][1:] + [t["sp"] if "Velocidade" in modo_enviado else 0.0]
        buffers[eixo]["sp_vq"]  = buffers[eixo]["sp_vq"][1:]  + [t["sp"] if ("Seno" in modo_enviado or "Quadrada" in modo_enviado) else 0.0]

    # Atualização de ecrãs de gráficos
    curve_p_pos.setData(x_axis, buffers["P"]["pos"]); curve_p_sp_pos.setData(x_axis, buffers["P"]["sp_pos"])
    curve_p_vel.setData(x_axis, buffers["P"]["vel"]); curve_p_sp_vel.setData(x_axis, buffers["P"]["sp_vel"])
    curve_p_vq.setData(x_axis, buffers["P"]["vq"]);   curve_p_sp_vq.setData(x_axis, buffers["P"]["sp_vq"])
    
    curve_y_pos.setData(x_axis, buffers["Y"]["pos"]); curve_y_sp_pos.setData(x_axis, buffers["Y"]["sp_pos"])
    curve_y_vel.setData(x_axis, buffers["Y"]["vel"]); curve_y_sp_vel.setData(x_axis, buffers["Y"]["sp_vel"])
    curve_y_vq.setData(x_axis, buffers["Y"]["vq"]);   curve_y_sp_vq.setData(x_axis, buffers["Y"]["sp_vq"])

    # Atualização de Displays Digitais Independentes (Pitch / Yaw)
    if hasattr(window, 'label_Posicao_Pitch'): window.label_Posicao_Pitch.setText(f"{telemetria['pitch']['pos']:.2f}")
    if hasattr(window, 'label_Velocidade_Pitch'): window.label_Velocidade_Pitch.setText(f"{telemetria['pitch']['vel']:.2f}")
    if hasattr(window, 'label_tensao_q_Pitch'): window.label_tensao_q_Pitch.setText(f"{telemetria['pitch']['vq']:.2f}")
    if hasattr(window, 'label_tensao_d_Pitch'): window.label_tensao_d_Pitch.setText(f"{telemetria['pitch']['vd']:.2f}")

    if hasattr(window, 'label_Posicao_Yaw'): window.label_Posicao_Yaw.setText(f"{telemetria['yaw']['pos']:.2f}")
    if hasattr(window, 'label_Velocidade_Yaw'): window.label_Velocidade_Yaw.setText(f"{telemetria['yaw']['vel']:.2f}")
    if hasattr(window, 'label_tensao_q_Yaw'): window.label_tensao_q_Yaw.setText(f"{telemetria['yaw']['vq']:.2f}")
    if hasattr(window, 'label_tensao_d_Yaw'): window.label_tensao_d_Yaw.setText(f"{telemetria['yaw']['vd']:.2f}")


# --- ENVIO COMPACTO DE PARÂMETROS ---
def enviar_parametros_esp32():
    global modo_enviado, cmd_gravar_global

    modo_texto = window.comboBox_setpoint.currentText()
    modo_enviado = modo_texto 
    
    # Leitura isolada de Amplitudes e Frequências da UI
    amp_pitch = window.doubleSpinBox_amplitude_Pitch.value() if hasattr(window, 'doubleSpinBox_amplitude_Pitch') else 0.0
    freq_pitch = window.doubleSpinBox_frequencia_Pitch.value() if hasattr(window, 'doubleSpinBox_frequencia_Pitch') else 0.0
    amp_yaw = window.doubleSpinBox_amplitude_Yaw.value() if hasattr(window, 'doubleSpinBox_amplitude_Yaw') else 0.0
    freq_yaw = window.doubleSpinBox_frequencia_Yaw.value() if hasattr(window, 'doubleSpinBox_frequencia_Yaw') else 0.0

    modo_id = 1 if "Seno" in modo_texto else 2 if "Quadrada" in modo_texto else 3 if "Posição" in modo_texto else 4
    setpoint_Pitch = amp_pitch if modo_id in [1,2] else window.doubleSpinBox_pos_veloc_Pitch.value()
    setpoint_Yaw = amp_yaw if modo_id in [1,2] else window.doubleSpinBox_pos_veloc_Yaw.value()


    # Leitura dinâmica dos ganhos PID
    kp_pitch = window.doubleSpinBox_Pitch_Kp.value() if hasattr(window, 'doubleSpinBox_Pitch_Kp') else 0.0
    ki_pitch = window.doubleSpinBox_Pitch_Ki.value() if hasattr(window, 'doubleSpinBox_Pitch_Ki') else 0.0
    kd_pitch = window.doubleSpinBox_Pitch_Kd.value() if hasattr(window, 'doubleSpinBox_Pitch_Kd') else 0.0
    kp_yaw = window.doubleSpinBox_Yaw_Kp.value() if hasattr(window, 'doubleSpinBox_Yaw_Kp') else 0.0
    ki_yaw = window.doubleSpinBox_Yaw_Ki.value() if hasattr(window, 'doubleSpinBox_Yaw_Ki') else 0.0
    kd_yaw = window.doubleSpinBox_Yaw_Kd.value() if hasattr(window, 'doubleSpinBox_Yaw_Kd') else 0.0
    
    # Conversão e leitura linear dos Filtros Passa-Baixo através das ScrollBars
    lpf_pitch = window.horizontalScrollBar_LPF_Pitch.value() / 100.0 if hasattr(window, 'horizontalScrollBar_LPF_Pitch') else 0.0
    lpf_yaw = window.horizontalScrollBar_LPF_Yaw.value() / 100.0 if hasattr(window, 'horizontalScrollBar_LPF_Yaw') else 0.0

    malhafechada = window.checkBox_loop.isChecked()
    
    # Transmissão do frame binário de 53 bytes rumo ao microcontrolador
    serial_worker.send_cmd(modo_id, malhafechada, cmd_gravar_global, kp_pitch, ki_pitch, kd_pitch, lpf_pitch, kp_yaw, ki_yaw, kd_yaw, lpf_yaw, setpoint_Pitch, setpoint_Yaw, freq_pitch, freq_yaw)


# --- PROCESSAMENTO EXCLUSIVO DA BLACKBOX (DESCARGA COMPLETA) ---
@Slot(list)
def processar_pacote_log(linha_dados):
    global cmd_gravar_global, is_recording
    ts = linha_dados[0]
    
    if ts == 4294967295:  # Sinalizador de término enviado pelo ESP32 (0xFFFFFFFF)
        print("Toda a memória interna da Blackbox foi descarregada. A exportar arquivo...")
        save_to_csv()
        window.botao_dados.setText("Gravar Dados")
        window.botao_dados.setStyleSheet("")
        cmd_gravar_global = 0
        enviar_parametros_esp32()  # Sincroniza estado de repouso no ESP32
    else:
        recorded_data.append(linha_dados)


def toggle_recording():
    global is_recording, recorded_data, cmd_gravar_global
    if not is_recording:
        recorded_data = [] 
        is_recording = True
        cmd_gravar_global = 1  # Sinal de início de gravação na RAM do ESP32
        window.botao_dados.setText("a Gravar")
        window.botao_dados.setStyleSheet("background-color: #e74c3c; font-weight: bold; color: white;")
        print("Sinal emitido: Gravação em tempo real ativa no Core 0 do ESP32.")
        enviar_parametros_esp32()
    else:
        is_recording = False
        cmd_gravar_global = 2  # Sinal de paragem e ordem de dump imediato
        window.botao_dados.setText("A Descarregar Dados...")
        window.botao_dados.setStyleSheet("background-color: #f39c12; font-weight: bold; color: white;")
        enviar_parametros_esp32()


def save_to_csv():
    global recorded_data
    if not recorded_data: return
    filename = f"./App debug/ensaio_motor_{int(time.time())}.csv"
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp_ms', 'SP_Pitch', 'Pos_Pitch', 'Vel_Pitch', 'Vq_Pitch', 'Vd_Pitch', 'SP_Yaw', 'Pos_Yaw', 'Vel_Yaw', 'Vq_Yaw', 'Vd_Yaw'])
            writer.writerows(recorded_data)
        print(f"Sucesso: Ensaio consolidado guardado em '{filename}'")
    except Exception as e:
        print(f"Erro crítico ao estruturar CSV: {e}")


# --- FUNÇÕES DE SINCRONIZAÇÃO EM TEMPO REAL DOS SLIDERS LPF ---
def atualizar_lpf_pitch(valor_inteiro):
    window.label_LPF_Pitch.setText(f"{(valor_inteiro / 100.0):.2f}")

def atualizar_lpf_yaw(valor_inteiro):
    window.label_LPF_Yaw.setText(f"{(valor_inteiro / 100.0):.2f}")


# --- GESTÃO VISUAL DINÂMICA DE LAYOUT DE ACORDO COM O MODO ---
def alterar_modo_sinal():
    m = window.comboBox_setpoint.currentText()
    vis_pos_vel = "Posição" in m or "Velocidade" in m
    window.doubleSpinBox_pos_veloc_Pitch.setVisible(vis_pos_vel); window.doubleSpinBox_pos_veloc_Yaw.setVisible(vis_pos_vel)
    window.doubleSpinBox_frequencia_Pitch.setVisible(not vis_pos_vel); window.doubleSpinBox_amplitude_Pitch.setVisible(not vis_pos_vel)
    window.doubleSpinBox_frequencia_Yaw.setVisible(not vis_pos_vel); window.doubleSpinBox_amplitude_Yaw.setVisible(not vis_pos_vel)

def handle_serial_error(err_msg):
    print(f"ERRO SÉRIAL: {err_msg}")


# --- INICIALIZAÇÃO DA COMUNICAÇÃO ASSÍNCRONA TRABALHADORA ---
serial_worker = SerialManager(port='/dev/ttyACM0', baudrate=921600)  # Operação a alta velocidade (Otimizado)
serial_worker.data_received.connect(update_ui_with_real_data)
serial_worker.error_occurred.connect(handle_serial_error)
serial_worker.log_data_received.connect(processar_pacote_log)
serial_worker.start()

# --- INSTANCIAÇÃO DOS EVENTOS DA INTERFACE (MÁQUINA QT) ---
window.botao_dados.clicked.connect(toggle_recording)
window.comboBox_setpoint.currentIndexChanged.connect(alterar_modo_sinal)
window.horizontalScrollBar_LPF_Pitch.valueChanged.connect(atualizar_lpf_pitch)
window.horizontalScrollBar_LPF_Yaw.valueChanged.connect(atualizar_lpf_yaw)

if hasattr(window, 'pushButton_enviar'):
    window.pushButton_enviar.clicked.connect(enviar_parametros_esp32)
if hasattr(window, 'pushButton_aplicar'):
    window.pushButton_aplicar.clicked.connect(enviar_parametros_esp32)

# Forçar o alinhamento visual inicial correto das abas antes da exibição
alterar_modo_sinal()
window.show()
sys.exit(app.exec())