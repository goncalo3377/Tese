%% Script MATLAB: Identificação do Pitch com Deteção Automática de Frequência
clear; clc; close all;

% =========================================================================
% CONFIGURAÇÃO DIRETÓRIO E COLUNAS
% =========================================================================

% Pasta onde estão os teus CSVs ('.' significa a pasta atual)
pasta_dados = ['./ensaio_1_yaw']; 

% Procurar todos os ficheiros .csv na pasta
lista_csv = dir(fullfile(pasta_dados, '*.csv'));
num_frequencias = length(lista_csv);

if num_frequencias == 0
    error('Nenhum ficheiro CSV encontrado na pasta: %s', pasta_dados);
end

% Mapeamento das colunas do teu CSV
idx_tempo   = 1; % Timestamp_ms
idx_saida   = 8; % Pos_Pitch 3 ou 8
idx_entrada = 10; % Vq_Pitch 5 ou 10

% Inicializar vetores para armazenar os resultados de cada ficheiro
w_vetor_dados = zeros(num_frequencias, 1);
magnitudes_db = zeros(num_frequencias, 1);
fases_graus = zeros(num_frequencias, 1);
ficheiros_validos = cell(num_frequencias, 1);

fprintf('A processar ficheiros e a detetar frequências automaticamente...\n\n');

for i = 1:num_frequencias
    caminho_completo = fullfile(pasta_dados, lista_csv(i).name);
    dados = readmatrix(caminho_completo); 
    
    t = dados(:, idx_tempo) / 1000; % Converte ms para segundos
    u = dados(:, idx_entrada);     % Vq_Pitch (Entrada)
    y = dados(:, idx_saida);       % Pos_Pitch (Saída)
    
    % ---------------------------------------------------------------------
    % DETEÇÃO AUTOMÁTICA DA FREQUÊNCIA (Via FFT no sinal de entrada)
    % ---------------------------------------------------------------------
    N = length(t);
    dt = mean(diff(t)); % Tempo de amostragem médio
    Fs = 1 / dt;        % Frequência de amostragem em Hz
    
    % Remover o valor médio (DC) para o pico do sinal não ser ofuscado
    u_detrend = u - mean(u); 
    
    % Calcular a FFT do sinal de entrada
    Y_fft = fft(u_detrend);
    P2 = abs(Y_fft / N);
    P1 = P2(1:floor(N/2)+1);
    P1(2:end-1) = 2*P1(2:end-1);
    
    % Vetor de frequências em Hz
    f_vetor = Fs * (0:(floor(N/2))) / N;
    
    % Encontrar o índice onde a amplitude é máxima (frequência dominante)
    [~, idx_max] = max(P1);
    f_detetada_hz = f_vetor(idx_max);
    
    % Converter para velocidade angular (rad/s)
    w = 2 * pi * f_detetada_hz;
    
    % Se a frequência detetada for zero ou infinitesimal (ruído), ignora
    if w < 0.01
        fprintf('Aviso: Ficheiro "%s" ignorado (sinal estático ou sem oscilação relevante).\n', lista_csv(i).name);
        continue;
    end
    
    w_vetor_dados(i) = w;
    ficheiros_validos{i} = caminho_completo;
    
    % ---------------------------------------------------------------------
    % PROCESSAMENTO DOS SINAIS (Mínimos Quadrados com a frequência detetada)
    % ---------------------------------------------------------------------
    M = [sin(w*t), cos(w*t), ones(size(t))];
    coef_u = M \ u;
    coef_y = M \ y;
    
    Amp_in  = sqrt(coef_u(1)^2 + coef_u(2)^2);
    Amp_out = sqrt(coef_y(1)^2 + coef_y(2)^2);
    
    fase_in  = atan2(coef_u(2), coef_u(1));
    fase_out = atan2(coef_y(2), coef_y(1));
    
    magnitudes_db(i) = 20 * log10(Amp_out / Amp_in);
    diff_fase = atan2(sin(fase_out - fase_in), cos(fase_out - fase_in));
    fases_graus(i) = rad2deg(diff_fase);
    
    fprintf('Ficheiro: %s -> Frequência Detetada: %.3f rad/s (%.2f Hz)\n', ...
        lista_csv(i).name, w, f_detetada_hz);
end

% Limpar entradas vazias (caso algum ficheiro tenha sido ignorado)
indices_validos = w_vetor_dados > 0;
w_vetor = w_vetor_dados(indices_validos);
magnitudes_db = magnitudes_db(indices_validos);
fases_graus = fases_graus(indices_validos);

% CRUCIAL: Ordenar os vetores por ordem crescente de frequência para o diagrama de Bode
[w_vetor, idx_ordenacao] = sort(w_vetor);
magnitudes_db = magnitudes_db(idx_ordenacao);
fases_graus = fases_graus(idx_ordenacao);

% =========================================================================
% ESTIMAÇÃO DA FUNÇÃO DE TRANSFERÊNCIA
% =========================================================================
amp_absoluta = 10.^(magnitudes_db / 20);
H_jw = amp_absoluta .* exp(1i * deg2rad(fases_graus));

% Multiplicação por 'j*w' para anular o integrador (polo na origem)
H_jw_ajustado = H_jw .* (1i * w_vetor);
sys_frd_ajustado = frd(H_jw_ajustado, w_vetor);

fprintf('\nA estimar a dinâmica contínua do Pitch...\n');
sys_1ordem = tfest(sys_frd_ajustado, 1, 0);

% Recolocar o polo na origem (dividir por s)
s = tf('s');
G_s = sys_1ordem / s;

% =========================================================================
% RESULTADOS E GRÁFICOS
% =========================================================================
fprintf('\n==================================================\n');
fprintf('FUNÇÃO DE TRANSFERÊNCIA ESTIMADA - PITCH G(s):\n');
fprintf('==================================================\n');
display(G_s);

[num, den] = tfdata(G_s, 'v');
polo_real = -den(2)/den(1);
ganho_K = num(end);

fprintf('Polo integrado (origem): s = 0\n');
fprintf('Segundo polo do Pitch:       s = %.3f rad/s\n', polo_real);
fprintf('Ganho do sistema (K):        %.3f\n\n', ganho_K);

% Gerar o Gráfico de Bode final
figure('Name', 'Identificação Automática do Gimbal');
sys_frd_original = frd(H_jw, w_vetor);
bode(sys_frd_original, 'ro', G_s, 'b-'); 
grid on;
legend('Dados Extraídos dos CSVs', 'Modelo Estimado G(s)', 'Location', 'best');

%%
pidTuner(G_s, 'PID')

%%
%tirar o s para passar para velocidade
% 1. Defina a variável 's' como função de transferência
s = tf('s');

% 2. Crie a função contendo o termo 1/s
G_s2 = G_s *s;
pidTuner(G_s2)