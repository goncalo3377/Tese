import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# =========================================================================
#   FUNÇÃO AUXILIAR: DETETAR CRUZAMENTOS POR ZERO (SUBIDA)
# =========================================================================
def obter_cruzamentos_zero_subida(tempo, sinal):
    """
    Encontra os instantes exatos (segundos) onde o sinal cruza o zero a subir
    usando interpolação linear para máxima precisão.
    """
    cruzamentos = []
    # Deteta onde o sinal passa de negativo (ou zero) para positivo
    indices = np.where((sinal[:-1] <= 0) & (sinal[1:] > 0))[0]
    
    for idx in indices:
        t0, t1 = tempo[idx], tempo[idx+1]
        s0, s1 = sinal[idx], sinal[idx+1]
        # Interpolação linear: t_zero = t0 - s0 * (t1 - t0) / (s1 - s0)
        t_zero = t0 - s0 * (t1 - t0) / (s1 - s0)
        cruzamentos.append(t_zero)
        
    return np.array(cruzamentos)

# =========================================================================
#   CONFIGURAÇÕES DO ENSAIO
# =========================================================================
pasta_csv = './App debug/tensao/yaw/ensaio_1'  
eixo_analise = 'Yaw'              
tipo_entrada = 'Tensão'             

if not os.path.exists(pasta_csv):
    raise FileNotFoundError(f"Erro: A pasta '{pasta_csv}' não foi encontrada.")

arquivos = glob.glob(os.path.join(pasta_csv, '*.csv'))
if not arquivos:
    raise FileNotFoundError(f"Erro: Nenhum ficheiro .csv encontrado em '{pasta_csv}'.")

print(f"A processar {len(arquivos)} ensaios do eixo {eixo_analise} (Entrada: {tipo_entrada})...\n")

dados_resumo = []

# =========================================================================
#   LOOP DE LEITURA E EXTRAÇÃO GEOMÉTRICA DE VARIÁVEIS
# =========================================================================
for arq in arquivos:
    df = pd.read_csv(arq)
    t = df['Timestamp_ms'].values / 1000.0  
    
    if eixo_analise.lower() == 'pitch':
        out_sinal = df['Pos_Pitch'].values
        in_sinal = df['Vq_Pitch'].values if tipo_entrada == 'Tensão' else df['SP_Pitch'].values
    else:
        out_sinal = df['Pos_Yaw'].values
        in_sinal = df['Vq_Yaw'].values if tipo_entrada == 'Tensão' else df['SP_Yaw'].values
        
    # Centralizar as ondas removendo a componente DC (Crucial para o cruzamento por zero ser real)
    u = in_sinal - np.mean(in_sinal)
    y = out_sinal - np.mean(out_sinal)
    
    # 1. Amplitude geométrica pura (Pico)
    amp_in = 3
    amp_out = (np.max(y) - np.min(y)) / 2.0
    
    if amp_in == 0:
        continue
        
    ganho_linear = amp_out / amp_in
    mag_db = 20 * np.log10(ganho_linear)
    
    # Detetar picos apenas para calcular o Período T da entrada de forma estável
    picos_u, _ = find_peaks(u, height=0, prominence=np.max(u)*0.1)
    if len(picos_u) < 2:
        print(f" -> [Aviso] Ficheiro '{os.path.basename(arq)}' ignorado: picos de entrada insuficientes.")
        continue
        
    periodo_T = np.mean(np.diff(t[picos_u]))
    f_hz = 1.0 / periodo_T
    
    # --- ALTERAÇÃO PRINCIPAL: Determinação do atraso pelo Cruzamento por Zero ---
    zeros_u = obter_cruzamentos_zero_subida(t, u)
    zeros_y = obter_cruzamentos_zero_subida(t, y)
    
    if len(zeros_u) < 1 or len(zeros_y) < 1:
        print(f" -> [Aviso] Ficheiro '{os.path.basename(arq)}' ignorado: sem cruzamentos por zero suficientes.")
        continue
        
    atrasos = []
    for z_u in zeros_u:
        # Encontrar o primeiro cruzamento por zero da saída que ocorre DEPOIS da entrada
        zeros_y_posteriores = zeros_y[zeros_y > z_u]
        if len(zeros_y_posteriores) > 0:
            z_y_seguinte = zeros_y_posteriores[0]
            # Proteção: garantir que o cruzamento detetado pertence ao mesmo ciclo (menor que um período)
            if (z_y_seguinte - z_u) < periodo_T:
                atrasos.append(z_y_seguinte - z_u)
            
    if not atrasos:
        print(f" -> [Aviso] Ficheiro '{os.path.basename(arq)}' ignorado: falha ao emparelhar cruzamentos por zero.")
        continue
        
    dt = np.mean(atrasos)
    fase_deg = - (dt / periodo_T) * 360.0
    
    dados_resumo.append({
        'Ficheiro': os.path.basename(arq),
        'Freq_Hz': f_hz,
        'Amp_In': amp_in,
        'Amp_Out': amp_out,
        'Ganho_Lin': ganho_linear,
        'Bode_Mag_dB': mag_db,
        'Periodo_T_s': periodo_T,
        'Atraso_dt_s': dt,
        'Bode_Fase_deg': fase_deg
    })

# =========================================================================
#   CONSTRUÇÃO DA TABELA FINAL E ORDENAÇÃO
# =========================================================================
df_final = pd.DataFrame(dados_resumo)
df_final = df_final.sort_values(by='Freq_Hz').reset_index(drop=True)

print("\n" + "="*115)
print("   ESTAÇÃO DE TRATAMENTO DE ENSAIOS: VALORES EXTRAÍDOS POR CRUZAMENTO POR ZERO")
print("="*115)
print(df_final.to_string(index=False, formatters={
    'Freq_Hz': '{:6.2f}'.format,
    'Amp_In': '{:6.3f}'.format,
    'Amp_Out': '{:6.3f}'.format,
    'Ganho_Lin': '{:6.4f}'.format,
    'Bode_Mag_dB': '{:6.2f}'.format,
    'Periodo_T_s': '{:6.4f}'.format,
    'Atraso_dt_s': '{:6.4f}'.format,
    'Bode_Fase_deg': '{:6.1f}'.format
}))
print("="*115)

# =========================================================================
#   GERAR O DIAGRAMA DE BODE EXPERIMENTAL (EIXO X EM HZ)
# =========================================================================
plt.figure(figsize=(10, 8))
plt.clf()

# Sub-gráfico 1: Magnitude (dB)
ax1 = plt.subplot(2, 1, 1)
plt.semilogx(df_final['Freq_Hz'], df_final['Bode_Mag_dB'], 'r-o', linewidth=2, markersize=6)
plt.grid(True, which="both", ls="-", color='0.7')
plt.title(f"Diagrama de Bode Experimental (Cruzamento por Zero) - Eixo {eixo_analise}", fontsize=14)
plt.ylabel("Magnitude (dB)", fontsize=12)

# Sub-gráfico 2: Fase (Graus º)
ax2 = plt.subplot(2, 1, 2)
plt.semilogx(df_final['Freq_Hz'], df_final['Bode_Fase_deg'], 'b-o', linewidth=2, markersize=6)
plt.grid(True, which="both", ls="-", color='0.7')
plt.ylabel("Fase (Graus º)", fontsize=12)
plt.xlabel("Frequência (Hz)", fontsize=12)
fase_min = df_final['Bode_Fase_deg'].min()
fase_max = df_final['Bode_Fase_deg'].max()
fase_range = fase_max - fase_min

# Se todos os ensaios tiverem exatamente a mesma fase, evita divisão por zero
if fase_range == 0:
    fase_range = 10  # Define uma folga padrão de 10 graus

# Define os limites dinâmicos com 15% de folga acima e abaixo
plt.ylim([fase_min - 0.15 * fase_range, fase_max + 0.15 * fase_range])
# --------------------------------------------

from matplotlib.ticker import ScalarFormatter
ax1.xaxis.set_major_formatter(ScalarFormatter())
ax2.xaxis.set_major_formatter(ScalarFormatter())



plt.tight_layout()
plt.show()