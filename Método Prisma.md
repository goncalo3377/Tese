

Base de dados: scopus.com https://scholar.google.com https://ieeexplore.ieee.org/Xplore/home.jsp https://www.webofscience.com/wos/alldb/smart-search https://dl.acm.org https://link.springer.com

## Metodo PIO

### Population:
Incide sobre Drones e UAV
### Intervention:
solução técnica, o hardware ou o algoritmo aplicado sobre o problema (Population)

gimbal 2eixos **AND** ("Camera" RGB **OR** Visão computacional) **AND** laser
### Comparator:
N me faz sentido e o LLM diz que é opcional.

### Outcome:

Erro **OR** Latência **OR** Precisão de deteção ($mAP$)


### String final de Pesquisa:
```
("UAV" OR "UAS" OR "Drone" OR "Unmanned Aerial Vehicle") AND ("Gimbal" OR "2 axis" OR "two-axis" OR "Pitch-Roll") AND ("RGB" OR "Computer Vision" OR "Object Tracking" OR "Target Following") AND ("Laser" OR "Directed Energy") AND ("Accuracy" OR "Latency" OR "Error" OR "mAP") AND ("anti-drone" OR "anti drone" OR "Counter-UAS")
```

Aparece alguns artigos sobre gimbals em drones:

```
("UAV" OR "UAS" OR "Drone" OR "Unmanned Aerial Vehicle") AND ("Gimbal" OR "2 axis" OR "two-axis" OR "Pitch-Roll") AND ("RGB" OR "Computer Vision" OR "Object Tracking" OR "Target Following") AND ("Laser" OR "Directed Energy") AND ("Accuracy" OR "Latency" OR "Error" OR "mAP") AND ("anti-drone" OR "anti drone" OR "Counter-UAS") NOT ("Payload")
```



Papers que apareceram:
google schoolar = 57
IEEE explorer   = 0
Web of Science  = 100
acm             = 0
Springer Nature = 2

Papers relevantes
https://link.springer.com/chapter/10.1007/978-3-031-92011-0_15
https://ieeexplore.ieee.org/abstract/document/9743918
https://ieeexplore.ieee.org/abstract/document/10424853
https://www.spiedigitallibrary.org/conference-proceedings-of-spie/13222/132220U/External-guidance-of-anti-drone-equipment-based-on-GPS-INS/10.1117/12.3038831.short
[ssrn-4485818.pdf]
https://www.preprints.org/frontend/manuscript/53241b6180fc0523b6d74dcf8a7ed4a6/download_pub (review!!)


("UAV" OR "UAS" OR "Drone" OR "Unmanned Aerial Vehicle") AND ("Gimbal" OR "2 axis" OR "two-axis" OR "Pitch-Roll") AND ("Laser") AND ("anti-drone" OR "anti drone" OR "Counter-UAS") NOT ("Payload")





para gimbal

- **Population (P):** Gimbal, Pan-tilt unit, 2-axis tracker, Rotational platform.
    
- **Intervention (I):** Control algorithms, PID, Visual Servoing, PWM (Pulse Width Modulation), PWM control, Kalman Filter, Sliding Mode Control (SMC).
    
- **Outcome (O):** UAV tracking, Drone interception, Precision, Latency reduction.

("Gimbal" OR "Pan-tilt" OR "Pitch-Yaw") AND ("Modulation") AND ("Tracking")



para deteção 

- **Population (P):** `UAV`, `Drone`, `Low-altitude aircraft`, `sUAS`.
    
- **Intervention (I):** `Ground-based detection`, `Optical sensors`, `RADAR`, `Acoustic arrays`, `RF sensing`, `YOLO`, `Deep Learning`.
    
- **Outcome (O):** `Detection range`, `False alarm rate`, `Classification accuracy`, `Elevation angle`.
    
- **Context (C):** `Terrestrial`, `Coastal`, `Maritime`, `Static platform`.

("UAV" OR "Drone") AND ("Detection" OR "Recognition") AND ("Real-time")

("Drone" OR "UAV") AND ("Detection") AND ("Ground-based" OR "Terrestrial" OR "Land-based" OR "Coastal") AND ("Optical" OR "Camera" OR "YOLO") -Air-to-air -Onboard