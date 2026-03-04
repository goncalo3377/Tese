
### 1. Momento de Inércia Total ($J_{yaw}$)

$$J_{yaw} = \sum (m_i \cdot r_i^2)$$

- $m_i$: Massa de cada componente (câmera, frame, cabos).
    
- $r_i$: Distância perpendicular de cada massa ao eixo de rotação.
    
- _Nota:_ Para geometrias complexas, extraia o $J_{zz}$ do seu software CAD (SolidWorks, Fusion 360).


$$J_{yaw} = m_i \cdot r_i^2$$


### 2. Binário de Aceleração ($T_{acc}$)

Determina quão rápido o gimbal consegue reagir (slew rate).

$$T_{acc} = J_{yaw} \cdot \alpha$$

- $\alpha$ (Aceleração Angular): Em $rad/s^2$. Define a responsividade do sistema.
    
    - Se precisar ir de 0 a $\omega_{max}$ em $t$ segundos: $\alpha \approx \frac{\omega_{max}}{t}$.



### 3. Binário de Desequilíbrio/Gravidade ($T_{grav}$)

$$T_{grav} = M_{total} \cdot g \cdot d \cdot \sin(\theta)$$

- $M_{total}$: Massa total rodada.
    
- $g$: Aceleração da gravidade ($9.81 m/s^2$).
    
- $d$: Distância (offset) entre o eixo de rotação e o CoM.
    
- $\theta$: Ângulo de inclinação da base em relação à gravidade (pior caso: 90°).
em principio será 0 ou próximo disso, assumir 10º pela inclinação do navio.


### 4. Binário de Atrito e Cablagem ($T_{fric}$)

Resistência dos rolamentos e a rigidez dos cabos que passam pelo eixo.

- Geralmente estimado empiricamente ou 10-15% do binário dinâmico se usar rolamentos de qualidade e _slip rings_.



### 5. Binário Total Requerido ($T_{req}$)

A soma de todos os componentes com um Fator de Segurança ($FS$).

$$T_{req} = (T_{acc} + T_{grav} + T_{fric}) \cdot FS$$

- **Recomendação:** Use um $FS$ entre **1.5 e 2.0** para garantir que o motor não opere no limite térmico ("stall current").


É necessário determinar os motores para o gimbal, normalmente utiliza-se BLDC pq:
- têm vários pólos e utilizam onda sinusoidal pura (assim não existe vibração de mudança passo)
- n têm folgas pq são acoplados directamente no motor (n têm engrenagens)
necessário determinar:
- **Torque de Manutenção (Holding Torque):** A capacidade do motor de segurar a câmara imóvel
- **Torque Dinâmico:** A força necessária para **acelerar**

## Requisitos

arbitrário:
- velocidade angular($\omega$) = $2 \pi$ rad/s = 60rpm
- aceleração angular ($\alpha$) = $\frac{\pi}{6}$ rad/s² =
- massa do gimbal ($m_{total}$)


## Determinar o Momento de Inércia ($I$)
$$I = \frac{1}{12} m (a^2 + b^2)$$

- Onde $a$ e $b$ são as dimensões perpendiculares ao eixo de rotação.
- de forma mais simples assumimos cada objeto como um rectângulo com as dimensões das extremidades. 

= 0 pq está tudo equilibrado.

## Determinar o ### Torque de Pico ($\tau_{pico}$)

$$\tau_{total} = (I \cdot \alpha) + \tau_{desequilíbrio} + \tau_{externo}$$



## Conjuntos Motor | Encoder | FOC

### 1º conjunto (baixa resolução)
- Motor: GM4108H-120T ou GM5208-24 (35.90$)
https://shop.iflight.com/ipower-motor-gm4108h-120t-brushless-gimbal-motor-pro217
- Enconder: AS5048A Magnetic Encoder 14bits + **Aluminum Case GM4108** (26.99$)
https://shop.iflight.com/as5048a-magnetic-encoder-pro262
- Controlador: SimpleBGC 32bit Extended (275.99$)
https://shop.iflight.com/basecam-simplebgc-32-bit-extended-encoder-version-gimbal-controller-pro276

### 2º conjunto
- Motor: GM4108H-120T ou GM5208-24 (35.90$)
https://shop.iflight.com/ipower-motor-gm4108h-120t-brushless-gimbal-motor-pro217
- Enconder: TLE5012B 15bits NT Motor Encoder V4.2 (€30,00) (n sei se vem com o iman)
https://gordiansystems.nl/products/nt-motor-encoder-v4-2
- Storm32 BGC V4.1 (€44,90)
https://gordiansystems.nl/products/storm32-bgc-v4-1?variant=52523878580557
