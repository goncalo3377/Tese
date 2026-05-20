import sys
import csv
import time
import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, Slot
from PySide6.QtUiTools import QUiLoader

# Importamos o nosso gestor de comunicação recém-criado
from communication import SerialManager

app = QApplication(sys.argv)

loader = QUiLoader()
loader.registerCustomWidget(PlotWidget)

file = QFile('./App debug/debug.ui')
file.open(QFile.ReadOnly)
window = loader.load(file)
file.close()

# Legendas dos Gráficos
window.widget_posicao.setLabel('left', 'Posição Ângulo', units='rad')
window.widget_posicao.setLabel('bottom', 'Amostras')
window.widget_velocidade.setLabel('left', 'Velocidade Angular', units='rad/s')
window.widget_velocidade.setLabel('bottom', 'Amostras')

# --- CONFIGURAÇÃO DOS DADOS E GRÁFICOS ---
x_axis = list(range(100))
data_pos = [0] * 100
data_vel = [0] * 100

is_recording = False      
recorded_data = []        
recording_start_time = 0  

window.widget_posicao.setBackground('#262829')
curve_pos = window.widget_posicao.plot(x_axis, data_pos, pen=pg.mkPen('b', width=2))

window.widget_velocidade.setBackground('#262829')
curve_vel = window.widget_velocidade.plot(x_axis, data_vel, pen=pg.mkPen('r', width=2))


# --- FUNÇÃO DE ATUALIZAÇÃO DA UI (CHAMADA VIA SINAL SÉRIE) ---
@Slot(dict)
def update_ui_with_real_data(telemetria):
    global data_pos, data_vel, is_recording, recorded_data, recording_start_time
    
    # 1. Atualizar buffers dos gráficos com dados REAIS vindos do ESP32
    data_pos = data_pos[1:] + [telemetria["posicao"]]
    data_vel = data_vel[1:] + [telemetria["velocidade"]]
    

    # 2. Atualizar as curvas
    curve_pos.setData(x_axis, data_pos)
    curve_vel.setData(x_axis, data_vel)
    
    # 3. Atualizar as labels digitais
    if hasattr(window, 'label_Posicao'):
        window.label_Posicao.setText(f"{telemetria['posicao']:.2f}")
    if hasattr(window, 'label_Velocidade'):
        window.label_Velocidade.setText(f"{telemetria['velocidade']:.2f}")
    if hasattr(window, 'label_tensao_q'):
        window.label_tensao_q.setText(f"{telemetria['tensao_q']:.2f}")
    if hasattr(window, 'label_tensao_d'):
        window.label_tensao_d.setText(f"{telemetria['tensao_d']:.2f}")

    # 4. Gravação de logs
    if is_recording:
        timestamp_relativo = int((time.time() - recording_start_time) * 1000)
        recorded_data.append([timestamp_relativo, telemetria['posicao'], telemetria['velocidade']])

    alterar_modo_sinal()


# --- ENVIAR PARÂMETROS PARA O ESP32 ---
def enviar_parametros_esp32():
    """Lê todos os valores configurados na interface e despacha-os via Serial"""
    # 1. Mapear qual o modo de setpoint selecionado (convertido para ID numérico)
    modo_texto = window.comboBox_setpoint.currentText()
    modo_id = 0
    setpoint = 0.0

    if modo_texto == "Seno":
        modo_id = 1
        setpoint = window.doubleSpinBox_amplitude.value() # Amplitude atua como setpoint dinâmico ou podes passar a frequência noutro campo
    elif modo_texto == "Quadrada":
        modo_id = 2
        setpoint = window.doubleSpinBox_amplitude.value()
    elif "Posição" in modo_texto:
        modo_id = 3
        setpoint = window.doubleSpinBox_pos_veloc.value() # Posição Alvo
    elif "Velocidade" in modo_texto:
        modo_id = 4
        setpoint = window.doubleSpinBox_pos_veloc.value() # Velocidade Alvo

    # 2. Capturar os ganhos PID e Filtros das caixas de texto (Verifica os objectNames no teu Designer!)
    # Como tens Pitch e Yaw, podes escolher qual enviar ou ler o valor adequado. Exemplo para Pitch:
    kp = window.doubleSpinBox_Kp_pitch.value() if hasattr(window, 'doubleSpinBox_Kp_pitch') else 0.0
    ki = window.doubleSpinBox_Ki_pitch.value() if hasattr(window, 'doubleSpinBox_Ki_pitch') else 0.0
    kd = window.doubleSpinBox_Kd_pitch.value() if hasattr(window, 'doubleSpinBox_Kd_pitch') else 0.0
    
    # Filtro do Encoder LPF (Ajusta para a tua doubleSpinBox real do filtro)
    lpf = window.doubleSpinBox_lpf_pitch.value() if hasattr(window, 'doubleSpinBox_lpf_pitch') else 0.0

    # 3. Disparar o envio via thread binária
    serial_worker.send_cmd(modo_id, kp, ki, kd, lpf, setpoint)
    print(f"Comando enviado: Modo={modo_id}, PID=({kp},{ki},{kd}), LPF={lpf}, SP={setpoint}")


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

def alterar_modo_sinal():
    modo = window.comboBox_setpoint.currentText()
    if "Posição" in modo:
        window.doubleSpinBox_pos_veloc.show()
        if hasattr(window, 'lbl_posicao_velocidade'): window.lbl_posicao_velocidade.show()
        window.doubleSpinBox_frequencia.hide()
        if hasattr(window, 'lbl_frequencia_texto'): window.lbl_frequencia_texto.hide()
        window.lbl_posicao_velocidade.setText("Posição (rad)")
        window.doubleSpinBox_amplitude.hide()
        if hasattr(window, 'lbl_amplitude_texto'): window.lbl_amplitude_texto.hide()
    elif "Velocidade" in modo:
        window.doubleSpinBox_pos_veloc.show()
        if hasattr(window, 'lbl_posicao_velocidade'): window.lbl_posicao_velocidade.show()
        window.doubleSpinBox_frequencia.hide()
        if hasattr(window, 'lbl_frequencia_texto'): window.lbl_frequencia_texto.hide()
        window.doubleSpinBox_amplitude.hide()
        if hasattr(window, 'lbl_amplitude_texto'): window.lbl_amplitude_texto.hide()
        window.lbl_posicao_velocidade.setText("Velocidade (rad/s)")
    else:
        window.doubleSpinBox_pos_veloc.hide()
        if hasattr(window, 'lbl_posicao_velocidade'): window.lbl_posicao_velocidade.hide()
        window.doubleSpinBox_frequencia.show()
        if hasattr(window, 'lbl_frequencia_texto'): window.lbl_frequencia_texto.show()
        window.doubleSpinBox_amplitude.show()
        if hasattr(window, 'lbl_amplitude_texto'): window.lbl_amplitude_texto.show()

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
# Conecta o teu botão de Aplicar do PID / Ondas para disparar a função de transmissão
if hasattr(window, 'btn_aplicar'):
    window.btn_aplicar.clicked.connect(enviar_parametros_esp32)

window.show()
sys.exit(app.exec())