Para construir um gimbal de dois eixos são necessário 4 componentes essenciais. Um motor, normalmente BLDC com muitos pólos para conseguir a resolução pretendida. Um encoder com resolução suficiente, normalmente magnético pelo seu custo benefício. Um controlador usualmente *field-oriented control* (FOC) para maior eficiência, maior torque em baixas velocidades e menor ruído. E por fim um driver que receberá as entradas do controlador e irá controlar os motores.

Inicialmente o objetivo seria conseguir obter uma exatidão de 5 cm num alvo a 200 m do gimbal, o que resulta numa resolução de 0.007º, que é difícil de alcançar com os componentes normalmente utilizados, para alcançar esta resolução seria necessário criar as próprias placas com circuitos. 

Para tal irá ser abordado 3 conjuntos:
1. Conjunto (baixa resolução, "Plug and play")
	- Motor: 2 GM4108H-120T ou GM5208-24 (35.90$)
	https://shop.iflight.com/ipower-motor-gm4108h-120t-brushless-gimbal-motor-pro217
	- Enconder: 2 AS5048A Magnetic Encoder 14bits + **Aluminum Case GM4108** (26.99$)
	https://shop.iflight.com/as5048a-magnetic-encoder-pro262
	- Controlador e Driver: SimpleBGC 32bit Extended (275.99$)
	https://shop.iflight.com/basecam-simplebgc-32-bit-extended-encoder-version-gimbal-controller-pro276
	**TOTAL** (convertido) = 345.53 euros sem logística
	
2. Conjunto (Barato) 
	- Motor: 2 GM4108H-120T ou GM5208-24 (35.90$)
	https://shop.iflight.com/ipower-motor-gm4108h-120t-brushless-gimbal-motor-pro217
	- Enconder: 2 TLE5012B 15bits NT Motor Encoder V4.2 (€30,00) (n sei se vem com o iman)
	https://gordiansystems.nl/products/nt-motor-encoder-v4-2
	- Controlador e Driver: Storm32 BGC V4.1 (€44,90)
	https://gordiansystems.nl/products/storm32-bgc-v4-1?variant=52523878580557
	**TOTAL** (convertido) = 146.7 euros sem logística
	
3. Conjunto (Do It Yourself (DIY))
	- Motor: 1 MITOOT 2206 100T (10.5€)
	https://pt.aliexpress.com/item/1005002058458786.html
	- Enconder: 1 MT6835 (5.7€)
	https://pt.aliexpress.com/item/1005008191455426.html
	- Controlador: ESP32-S3 (4.9€)
	https://pt.aliexpress.com/item/1005005051294262.html
	- Driver: 1 Módulo DRV8313 (4.4€) 
	https://pt.aliexpress.com/item/1005008554726258.html
	**TOTAL** = 25.5€ (1 motor)