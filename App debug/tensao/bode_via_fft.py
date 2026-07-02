import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================================================================
#   CONFIGURAÇÕES DO ENSAIO
# =========================================================================
pasta_csv = './App debug/tensao/yaw/7v/ensaio_1'  # Pasta onde tens os teus ficheiros .csv
eixo_analise = 'pitch'                # OpÇÕES: 'Pitch' ou 'Yaw'
tipo_entrada = 'Tensão'             # 'Tensão' (Vq) ou 'Posição' (SP - Malha Fechada)

if not os.path.exists(pasta_csv):
    raise FileNotFoundError(f"Erro: A pasta '{pasta_csv}' não foi encontrada.")

arquivos = glob.glob(os.path.join(pasta_csv, '*.csv'))
if not arquivos:
    raise FileNotFoundError(f"Erro: Nenhum ficheiro .csv encontrado em '{pasta_csv}'.")

print(f"A processar {len(arquivos)} ensaios via FFT (Eixo: {eixo_analise} | Entrada: {tipo_entrada})...\n")

dados_resumo = []

# =========================================================================
#   LOOP DE LEITURA E PROCESSAMENTO DETETOR POR FFT
# =========================================================================
for arq in arquivos:
    # Proteção para ignorar o ficheiro de resumo caso ele esteja na mesma pasta
    if 'resumo_bode_fft' in arq or 'resumo_bode_manual' in arq: 
        continue
        
    df = pd.read_csv(arq)
    t = df['Timestamp_ms'].values / 1000.0  # Converter ms para segundos
    N = len(t)
    
    # Seleção automática de canais baseada no CSV estruturado
    if eixo_analise.lower() == 'pitch':
        out_sinal = df['Pos_Pitch'].values
        in_sinal = df['Vq_Pitch'].values if tipo_entrada == 'Tensão' else df['SP_Pitch'].values
    else:
        out_sinal = df['Pos_Yaw'].values
        in_sinal = df['Vq_Yaw'].values if tipo_entrada == 'Tensão' else df['SP_Yaw'].values
        
    # Filtro Squelch: Ignorar eixos mortos/parados sem dinâmica relevante
    if (np.max(out_sinal) - np.min(out_sinal)) < 0.05:
        continue
        
    # Centralizar os sinais (Remover componente contínua DC para não poluir o Bin 0)
    u = in_sinal - np.mean(in_sinal)
    y = out_sinal - np.mean(out_sinal)
    
    # Passo de amostragem médio deste ensaio (dt)
    dt = np.mean(np.diff(t))
    
    # =========================================================================
    #   APLICAÇÃO DA FFT (FAST FOURIER TRANSFORM)
    # =========================================================================
    U_fft = np.fft.fft(u)
    Y_fft = np.fft.fft(y)
    freqs = np.fft.fftfreq(N, d=dt) # Vetor de frequências associado à FFT
    
    # Focar apenas no espetro positivo (ignora a componente DC no índice 0)
    metade_espetro = N // 2
    espetro_amplitude_input = np.abs(U_fft[1:metade_espetro])
    
    # Encontrar o índice (Bin) do pico máximo absoluto da excitação
    idx_dominante = np.argmax(espetro_amplitude_input) + 1
    
    # Extrair a frequência exata detetada por Fourier
    f_hz = freqs[idx_dominante]
    w_rads = 2 * np.pi * f_hz
    
    # Extração dos componentes complexos puros (Fasores) no bin de interesse
    U_complexo = U_fft[idx_dominante]
    Y_complexo = Y_fft[idx_dominante]
    
    # =========================================================================
    #   CÁLCULO DOS PARÂMETROS DE BODE DE ACORDO COM A MATRIZ DE FOURIER
    # =========================================================================
    # Magnitude: Relação de módulos lineares convertida para Decibéis (dB)
    ganho_linear = np.abs(Y_complexo) / np.abs(U_complexo)
    mag_db = 20 * np.log10(ganho_linear)
    
    # Fase: Diferença angular dos números complexos (Ângulo Saída - Ângulo Entrada)
    fase_rad = np.angle(Y_complexo) - np.angle(U_complexo)
    
    # Normalização trigonométrica do vetor resultante no quadrante [-pi, pi]
    fase_rad = np.arctan2(np.sin(fase_rad), np.cos(fase_rad))
    fase_deg = np.degrees(fase_rad)
    
    # Como o motor é um sistema físico causal, a resposta sofre atraso (fase negativa)
    if fase_deg > 10:  # Pequena tolerância para ruídos perto de 0º
        fase_deg -= 360.0
    elif fase_deg < -270:
        fase_deg += 360.0
        
    # Guardar os valores calculados por este ensaio
    dados_resumo.append({
        'Ficheiro': os.path.basename(arq),
        'Freq_Hz': f_hz,
        'Freq_rad_s': w_rads,
        'Bode_Mag_dB': mag_db,
        'Bode_Fase_deg': fase_deg
    })
    
    print(f" -> Processado: {os.path.basename(arq)} | f = {f_hz:6.2f} Hz | Mag = {mag_db:6.2f} dB | Fase = {fase_deg:6.1f}º")

# =========================================================================
#   ORDENAÇÃO CRESCENTE E EXPORTAÇÃO
# =========================================================================
df_final = pd.DataFrame(dados_resumo).sort_values(by='Freq_Hz').reset_index(drop=True)

# Guardar o relatório estruturado em CSV para usares nos anexos da tese
csv_saida = os.path.join(pasta_csv, 'resumo_bode_fft.csv')
df_final.to_csv(csv_saida, index=False)

print("\n" + "="*85)
print(f"   RELATÓRIO DE FOURIER CONSOLIDADO EM: '{csv_saida}'")
print("="*85)
print(df_final.to_string(index=False, formatters={
    'Freq_Hz': '{:6.2f}'.format,
    'Freq_rad_s': '{:6.2f}'.format,
    'Bode_Mag_dB': '{:6.2f}'.format,
    'Bode_Fase_deg': '{:6.1f}'.format
}))
print("="*85 + "\n")

# =========================================================================
#   DESENHO DO DIAGRAMA DE BODE DE FOURIER
# =========================================================================
plt.figure(figsize=(10, 8), facecolor='white')
w_min = np.min(df_final['Freq_rad_s']) * 0.8
w_max = np.max(df_final['Freq_rad_s']) * 1.2

# Sub-gráfico 1: Magnitude (dB)
plt.subplot(2, 1, 1)
plt.semilogx(df_final['Freq_rad_s'], df_final['Bode_Mag_dB'], 'm-o', linewidth=2, markersize=6, label='Espetro FFT')
plt.grid(True, which="both", ls="-", color='0.7')
plt.ylabel("Magnitude (dB)", fontsize=12)
plt.title(f"Diagrama de Bode por Fourier (FFT) - Eixo {eixo_analise}", fontsize=14)
plt.xlim([w_min, w_max])
plt.ylim([np.min(df_final['Bode_Mag_dB']) - 3, np.max(df_final['Bode_Mag_dB']) + 3])
plt.legend()

# Sub-gráfico 2: Fase (Graus º)
plt.subplot(2, 1, 2)
plt.semilogx(df_final['Freq_rad_s'], df_final['Bode_Fase_deg'], 'b-o', linewidth=2, markersize=6, label='Espetro FFT')
plt.grid(True, which="both", ls="-", color='0.7')
plt.ylabel("Fase (Graus º)", fontsize=12)
plt.xlabel("Frequência Angular (rad/s)", fontsize=12)
plt.xlim([w_min, w_max])
plt.ylim([-270, 10]) # Margem padrão de estabilidade académica
plt.legend()

plt.tight_layout()
plt.show()