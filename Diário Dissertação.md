O presente Trabalho de Dissertação foca-se na conceção, construção e validação experimental de um sistema gimbal de dois eixos, munido de uma configuração de câmaras RGB (simples ou estereoscópica), destinado à deteção e rastreio de Veículos Aéreos Não Tripulados (VANTs). Adicionalmente, o estudo inclui o dimensionamento teórico do sistema laser necessário para a funcionalidade de neutralização. A utilização de visão estereoscópica (duas câmeras) possibilita a visualização 3D do objeto (distância) enquanto que com apenas uma câmera permite apenas visualização 2D.   

## Ideias de Títulos
-  [Design of **anti**-**drone laser** weapon systems](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/11544/115440A/Design-of-anti-drone-laser-weapon-systems/10.1117/12.2575171.full?origin_id=x4323&start_year=2020&webSyncID=46e9e6ec-7a49-dab6-a0cb-ad059329ad88&sessionGUID=3c9d902b-c999-3ced-268b-ead49a28531a)
	  
- Conceção de sistema laser anti-drone (utilizando câmeras RGB)
	
- Desenvolvimento de um Sistema Gimbal de Seguimento Visual para Neutralização de UAV Utilizando Laser    
- de Laser  UAV (ou anti drone) (e Dimensionamento de Neutralização Laser)
	 
- Conceção de Unidade de Rastreio Estereoscópico e Análise Teórica de Eficácia Laser Anti-Drone

## Estruturação da Ideia

### O que se pretende fazer?

Pretende-se criar um sistema gimbal de dois eixos que com a utilização de câmeras RGB consiga detectar, seguir e abater ou neutralizar drones com a utilização de um laser. 
### Como é que é feito atualmente, e quais são as limitações correntes?

A nível empresarial temos:

- [Helios](https://www.lockheedmartin.com/content/dam/lockheed-martin/rms/documents/directed-energy/HELIOS_Infographic_FINAL.pdf) da Lockheed Martin ([apoio](https://www.youtube.com/watch?v=cvQV7Mt02q4), [WhitePaper](https://www.lockheedmartin.com/content/dam/lockheed-martin/rms/documents/directed-energy/HELIOS-WhitePaper-Dec-2021.pdf))
- [DE M-SHORAD](https://www.dote.osd.mil/Portals/97/pub/reports/FY2024/army/2024de_m-shorad.pdf?ver=aP_keA3PAt1C_pkWp_rAdQ%3D%3D)
- [Iron Beam](https://en.wikipedia.org/wiki/Iron_Beam)
- [DragonFire](https://en.wikipedia.org/wiki/DragonFire_(weapon))
- [Silent Hunter](https://en.wikipedia.org/wiki/Silent_Hunter_(laser_weapon))
- [Rheinmetall Laser](https://www.airforce-technology.com/contractors/air-defence/rheinmerallair/pressreleases/pressrheinmetall-tests-50kw-laser-weapon/)

Além do preço na cada das dezenas de milhões de euros, não são utilizados em modo totalmente autónomo e como tal também não têm foco em diferenciar uma gaivota de um Dji.
### Qual é a abordagem proposta e por que razão se pensa que será bem sucedida?

Dado o objetivo de baixo custo e mesmo assim não prescindir da precisão, o objetivo será utilizar câmaras RGB, motores de passo ou servo motores por forma a manter uma grande precisão do gimbal. Para a deteção utilizar yolo-drone ou outro algoritmo que obtenha melhores resultados na deteção de drones. Para o seguimento é necessário ainda **verificar o os algoritmos disponíveis**  
### A quem isso interessa? Em caso de sucesso que diferença fará?

Esta dissertação tenta trazer desenvolvimento em novos tipos de armas para a Marinha Portuguesa, mais baratas na utilização, para as novas ameaças de drones, onde não é vantajoso utilizar munições ou mísseis para abater um ou vários drones relativamente baratos.
Em caso de sucesso a marinha acresce o seu conhecimento neste tipo de sistemas, podendo mais tarde utilizar em navios, para abater drones ou utilizar no narcotráfico, utilizando o lazer para neutralizar as lanchas de alta velocidade. 
### Quais são os riscos?

A nível de riscos, esta dissertação não apresenta muitos riscos, dado que o dimensionamento do laser terá, por enquanto, caráter teórico. O risco mais comum de acontecer será o de danificação de material assim como o gasto de filamento. 
### Quanto custará?

A nível de custos ainda é muito difícil prever quanto será gasto no total, mas entre os custos estarão os custos de filamento, motores, câmaras RGB, lasers de demonstração e material de apoio como rolamentos, porcas, parafusos, etc.
### Quais são as avaliações finais e intermédias que definirão o sucesso do trabalho?

Para determinar o sucesso do meu trabalho pretendo que para avaliações intermédias seja possível implementar um algoritmos simples de deteção de drones e conseguir controlar o gimbal manualmente por forma a seguir o drone.

A nível de considerações finais, pretendo ter um algoritmo estável e robusto de deteção de drones que consiga diferenciar aves de drones na maior parte do tempo, pretendo também já ter um algoritmo de seguimento que acompanha o drone, controlando os motores para tal.



TIB-NET
YOLO DRONE

## Índice 
### Apoio
Estrutura do índice:
1. Problema do mundo real (contexto): Qual é o problema do mundo real, de uma forma geral, que será abordado? O que caracteriza este problema? Quais são as suas diferentes dimensões? 
2. Problema investigado: Qual é o problema em particular que se procurará resolver nesta dissertação? Quais são as suas principais vertentes? A que questões científicas principais se pretende responder no decurso do trabalho? 
3. Relevância: Por que razão este problema é relevante para a Marinha Portuguesa? O que pode a Marinha ganhar com este trabalho?
4. Objectivos: Quais são os objectivos deste trabalho? De que forma se pretende responder às questões de investigação colocadas? 

Apesar de não haver uma estrutura fixa para organizar este capítulo, uma abordagem típica consiste em dividir o mesmo nas seguintes secções:
1. Enquadramento / Contexto geral: facultar uma visão geral da área de investi- gação de forma a se perceber o problema geral em causa; 
2. Motivação: explicar por que razão o tópico investigado é importante, quais as limitações actuais, de que forma se pretende contribuir para colmatar essas limitações;
3. Formulação do problema: identificar claramente o problema específico que se pretende investigar, os desafios associados, a questão (ou questões) científica concreta que pretende abordar;
4. Objectivos: enunciar de forma clara e concreta o que se pretende atingir com a dissertação, quer a nível geral quer a nível de objectivos específicos.

### texto solto 

1. Com o constante desenvolvimento das tecnologias e as várias guerras que no presente decorrem é natural observar-se uma evolução nos sistemas de ataque. O que antes era feito utilizando mísseis ou torpedos que custam na casa dos milhões de euros agora é feito utilizando drones na ordem das dezenas de milhares de euros, "não me compreenda mal", os mísseis e os torpedos têm obviamente a sua função, mas quando se quer atacar o inimigo, o objetivo é causar o maior dano possível pelo menor custo possível e com os drones, mesmo não sendo tão efetivos, causam muito dano tendo em conta o seu custo tão reduzido. Essa evolução faz com que quem está a ser atacado também queira evoluir, dado que utilizar mísseis ou mesmo sistemas CIWS (close in weapon system) é desvantajoso pois quem está a ser atacado está a gastar muito mais dinheiro do que quem está a atacar com "simples brinquedos". 
   Assim como no caso de guerras, tem-se tambem muito presente o problema do narcotráfico que no seu último estágio utilizam lanchas de alta velocidade. A marinha portuguesa até pode conseguir detetar e seguir, mas neutralizar ainda é um grande problema, não podendo utilizar artelharia móvel dado a sua falta de precisão e utilizar a peça de artelharia além de ser desvantajoso a nível financeiro, também aprensenta o mesmo problema da artelharia móvel, dado que o objetivo é neutralizar e não causar mortes.
2. Para ser possível colmatar estas ameaças uma abordagem plausível a utilização de sistemas lasers para neutralizar drones ou até mesmo lanchas de narcotráfico. Um sistema laser tem uma grande vantagem em comparação ao métodos tradicionais de artilharia, pois estes inevitavelmente têm que consumir munições que podem ser escassas, enquanto que o lasers tem a vantagem de ser apenas necessário eletricidade, a coisa que é normalmente abundante em missões.
   Atualmente existem algumas marinhas que já utilizam sistemas completos a laser, quer seja nos EUA ou na China, estes sistemas estão já bem presentes em países bem desenvolvidos a nível militar. Esses sistemas já são extremamente desenvolvidos com integração com o radar para possível deteção e utilização de câmeras já integradas no sistema para fazer o seguimento.


## Título Decidido 
Desenvolvimento de um Sistema Gimbal de Seguimento Visual para Neutralização de UAV Utilizando Laser
