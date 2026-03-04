## Gimbal
- Abordar na construção do gimbal
- Tem 2 eixos
- Para cada eixo 1 motor
- Feito em impressora 3d e o pq
- Como será controlado, o que recebe e o que envia
- Utilização de 1 ou 2 câmeras
- Quais as diferenças entre o que é preciso fazer entre 1 câmera e duas e quais os problemas associados
- Cinemática inversa, como passo da posição do drone para os motores
- O que acontece com o ponteiro laser, onde está e como ficará
- Controlo pid para os motores 
## Visão computacional
- Utilizar uma nvidia jetson nano para numa primeira instância para ser o cérebro do projeto, onde será responsável por rodar os modelos de deteção e seguimento. 
- Calibrar a/as câmeras utilizando método do tabuleiro de xadrez (Zhang)
- Testar os modelos com datasets conhecidos para deixar a funcionar plenamente.
- criar um dataset de teste com drones a diferentes distâncias 5/10/25/50/75/100/150/200m
- verificar qual modelo apresenta uma melhor deteção para cada distância.
- criar datasets de drones a se movimentarem e determinar o erro de deteção da posição do drone para verificar qual modelo que já incorpora seguimento obtém melhor resultado.
  
## Incorporação de Módulos

- incorporar uma estimativa de movimento de onde o drone estará para o seu seguimento
- retirar a posição relativa do drone na imagem da camera e medir o erro de onde deverá estar para o laser acertar
- converter esse erro em ângulos de pitch e yaw e enviar para o pid dos motores.
- medir o erro de onde o laser está e de onde deveria estar.

## Laser

- calcular a potência e comprimento de onda para a queima de plástico a várias distâncias e com diferentes cores de plástico.
- efetuar um teste com laser para corte de mdf (talvez)
- retirar o erro entre a previsão e o ensaio real. (depende da anterior)


