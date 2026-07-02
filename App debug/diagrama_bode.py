import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# =========================================================================
#   CONFIGURAÇÕES DO ENSAIO
# =========================================================================
pasta_csv = './App debug/tensao/yaw/ensaio_1'  # Pasta onde tens os teus ficheiros .csv
eixo_analise = 'Yaw'              # Opções: 'Pitch' ou 'Yaw'
tipo_entrada = 'Tensão'             # 'Tensão' (Vq) ou 'Posição' (SP - Malha Fechada)

if not os.path.exists(pasta_csv):
    raise FileNotFoundError(f"Erro: A pasta '{pasta_csv}' não foi encontrada.")

arquivos = glob.glob(os.path.join(pasta_csv, '*.csv'))
if not arquivos:
    raise FileNotFoundError(f"Erro: Nenhum ficheiro .csv encontrado em '{pasta_csv}'.")

print(f"A processar {len(arquivos)} ensaios do eixo {eixo_analise} (Entrada: {tipo_entrada})...\n")

# Lista para acumular os dicionários de dados de cada ficheiro
dados_resumo = []

# =========================================================================
#   LOOP DE LEITURA E EXTRAÇÃO GEOMÉTRICA DE VARIÁVEIS
# =========================================================================
for arq in arquivos:
    df = pd.read_csv(arq)
    t = df['Timestamp_ms'].values / 1000.0  # Converter ms para segundos
    
    if eixo_analise.lower() == 'pitch':
        out_sinal = df['Pos_Pitch'].values
        in_sinal = df['Vq_Pitch'].values if tipo_entrada == 'Tensão' else df['SP_Pitch'].values
    else:
        out_sinal = df['Pos_Yaw'].values
        in_sinal = df['Vq_Yaw'].values if tipo_entrada == 'Tensão' else df['SP_Yaw'].values
        
    # Centralizar as ondas removendo a componente DC
    u = in_sinal - np.mean(in_sinal)
    y = out_sinal - np.mean(out_sinal)
    
    # 1. Amplitude geométrica pura (Pico)
    amp_in = (np.max(u) - np.min(u)) / 2.0
    amp_out = (np.max(y) - np.min(y)) / 2.0
    
    if amp_in == 0:
        continue
        
    ganho_linear = amp_out / amp_in
    mag_db = 20 * np.log10(ganho_linear)
    
    # 2. Detetar picos com filtros de proeminência para evitar ruído do encoder
    picos_u, _ = find_peaks(u, height=0, prominence=np.max(u)*0.01)
    
    picos_y, _ = find_peaks(y, height=0, prominence=np.max(y)*0.01)
    picos_y2, _ = find_peaks(y, height=0, prominence=np.max(y))
    print("picos y 0.2")
    print(picos_y)
    print("pico y sem nada")
    print(picos_y2)
    
    if len(picos_u) < 2 or len(picos_y) < 1:
        print(f" -> [Aviso] Ficheiro '{os.path.basename(arq)}' ignorado: picos insuficientes.")
        continue
        
    # Calcular o Período (T) médio do ensaio e a frequência correspondente
    periodo_T = np.mean(np.diff(t[picos_u]))
    f_hz = 1.0 / periodo_T
    w_rads = f_hz
    
    # Calcular o atraso dinâmico médio (dt) entre a excitação e a resposta
    atrasos = []
    for pk_u in picos_u:
        picos_y_posteriores = picos_y[picos_y > pk_u]
        if len(picos_y_posteriores) > 0:
            pk_y_seguinte = picos_y_posteriores[0]
            atrasos.append(t[pk_y_seguinte] - t[pk_u])
            
    dt = np.mean(atrasos)
    fase_deg = - (dt / periodo_T) * 360.0
    
    # Guardar todas as variáveis intermédias extraídas deste ensaio
    dados_resumo.append({
        'Ficheiro': os.path.basename(arq),
        'Freq_Hz': f_hz,
        'Freq_rad_s': w_rads,
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
# Ordenar de forma crescente pela frequência real detetada para o gráfico não cruzar
df_final = df_final.sort_values(by='Freq_Hz').reset_index(drop=True)

# 1. Mostrar a tabela formatada de forma profissional no terminal
print("\n" + "="*115)
print("   ESTAÇÃO DE TRATAMENTO DE ENSAIOS: VALORES EXTRAÍDOS GEOMETRICAMENTE (MÃO)")
print("="*115)
print(df_final.to_string(index=False, formatters={
    'Freq_Hz': '{:6.2f}'.format,
    'Freq_rad_s': '{:6.2f}'.format,
    'Amp_In': '{:6.3f}'.format,
    'Amp_Out': '{:6.3f}'.format,
    'Ganho_Lin': '{:6.4f}'.format,
    'Bode_Mag_dB': '{:6.2f}'.format,
    'Periodo_T_s': '{:6.4f}'.format,
    'Atraso_dt_s': '{:6.4f}'.format,
    'Bode_Fase_deg': '{:6.1f}'.format
}))
print("="*115)

# 2. Salvar a tabela em CSV para poderes usar no Excel / Dissertação
#csv_saida = os.path.join(pasta_csv, 'resumo_bode_manual.csv')
#df_final.to_csv(csv_saida, index=False)
#print(f"\n[Ficheiro Gerado] Todos os valores acima foram consolidados em: '{csv_saida}'")

# =========================================================================
#   GERAR O DIAGRAMA DE BODE EXPERIMENTAL
# =========================================================================
plt.figure(figsize=(10, 8))

# Sub-gráfico 1: Magnitude (dB)
plt.subplot(2, 1, 1)
plt.semilogx(df_final['Freq_rad_s'], df_final['Bode_Mag_dB'], 'r-o', linewidth=2, markersize=6)
plt.grid(True, which="both", ls="-", color='0.7')
plt.title(f"Diagrama de Bode Experimental Geométrico - Eixo {eixo_analise}", fontsize=14)
plt.ylabel("Magnitude (dB)", fontsize=12)
plt.legend(loc='best')

# Sub-gráfico 2: Fase (Graus º)
plt.subplot(2, 1, 2)
plt.semilogx(df_final['Freq_rad_s'], df_final['Bode_Fase_deg'], 'b-o', linewidth=2, markersize=6)
plt.grid(True, which="both", ls="-", color='0.7')
plt.ylabel("Fase (Graus º)", fontsize=12)
plt.xlabel("Frequência Angular (rad/s)", fontsize=12)
fase_min = df_final['Bode_Fase_deg'].min()
fase_max = df_final['Bode_Fase_deg'].max()
fase_range = fase_max - fase_min

# Se todos os ensaios tiverem exatamente a mesma fase, evita divisão por zero
if fase_range == 0:
    fase_range = 10  # Define uma folga padrão de 10 graus

# Define os limites dinâmicos com 15% de folga acima e abaixo
plt.ylim([fase_min - 0.15 * fase_range, fase_max + 0.15 * fase_range])

plt.tight_layout()
plt.show()