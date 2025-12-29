# 🤖 Controle de Mão Mecânica com MediaPipe

Este projeto utiliza a biblioteca **MediaPipe** para capturar e interpretar os movimentos da mão humana, traduzindo-os em comandos para controlar uma **mão mecânica**.  
O objetivo é explorar visão computacional e robótica de forma integrada.

---

## 🚀 Tecnologias Utilizadas
- [MediaPipe](https://developers.google.com/mediapipe) – Reconhecimento de gestos e landmarks da mão
- Python **3.11.9** – Versão utilizada no desenvolvimento
- OpenCV – Captura e manipulação de imagens da câmera
- Arduino Uno – Microcontrolador para controle da mão mecânica
- PySerial – Comunicação entre Python e Arduino

---

## 🔧 Requisitos de Hardware
Para reproduzir este projeto, você precisará dos seguintes componentes:

- 🖐️ **Mão mecânica** com **5 servos motores** (um para cada dedo)  
- ⚡ **Fonte HW-131** para alimentação no protoboard  
- 🎥 **Webcam** (utilizada a do notebook)  
- 🔌 **Arduino Uno**  
- 🔗 **Protoboard**  
- 🧵 **Jumpers** para conexões entre os componentes  

---

## Código Principal💻
```
''''Bibliotecas cv2 (opencv) usada para a capturar o vídeo da webcam
    Biblioteca mediapipe para Detecção e rastreamento de mãos
'''
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import serial

arduino = serial.Serial('COM8', 9600)

base_options = python.BaseOptions(model_asset_path="hand_landmarker.task") # hand_landmarker.task). Esse arquivo contém a rede neural treinada para detectar mãos.
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1) #configura como o detector de mãos vai funcionar, no meu caso eu coloquei 1 pois so quero uma mão
detector = vision.HandLandmarker.create_from_options(options) #cria o objeto detector, que é quem realmente roda a inferência (detecção).

cap = cv2.VideoCapture(0) # variável para abrir webcam no caso do meu pc so tem uma então coloquei 0

'''Aqui iremos conectar os pontos na mão
 onde colocamos tuplas ligados os pontos
 '''
HARD_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20)
]

while True:
    ret, frame = cap.read() # lê um frame da web-cam, ret indica se a leitura foi bem-sucedida
    if not ret: # ret == false então o while para
        break


    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)# aqui faz a conversao para o formato que o mediapipe entende
    result = detector.detect(mp_image) # serve para detectar mãos no frame

    if result.hand_landmarks:
        for hand_landmark in result.hand_landmarks: # aqui desenha os pontos da mão
            for landmark in hand_landmark:
                h, w, _ = frame.shape
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1) # desenha um círculo verde ((0,255,0)) com raio 5

            for connection in HARD_CONNECTIONS: # aqui desenha as conexões
                start = hand_landmark[connection[0]]
                end = hand_landmark[connection[1]]
                x1, y1 = int(start.x * w), int(start.y * h)
                x2, y2 = int(end.x * w), int(end.y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) # desenha um círculo verde ((0,255,0)) com raio 5

                servo_angles = []  # lista vazia para guardar os ângulos de cada servo
                # que vai ser recebido abaixo

                # Polegar
                if hand_landmark[4].x < hand_landmark[2].x:  # 4 ponta do polegar 2 base polegar
                    servo_angles.append(150)  # fechado
                else:
                    servo_angles.append(0)  # aberto

                # Indicador
                servo_angles.append(0 if hand_landmark[8].y < hand_landmark[
                    6].y else 180)  # 8 ponta do indicador 6 articulação do indicador.
                '''assim por diante'''
                # Médio
                servo_angles.append(0 if hand_landmark[12].y < hand_landmark[10].y else 180)
                # Anelar
                servo_angles.append(0 if hand_landmark[16].y < hand_landmark[14].y else 180)
                # Mínimo
                servo_angles.append(0 if hand_landmark[20].y < hand_landmark[18].y else 180)

                # envia para o Arduino
                arduino.write(
                    f"{','.join(map(str, servo_angles))}\n".encode())  # aqui faz o envio para o arduino, map transforma cada número em string
                # junta todos os valores separados por vírgula
                # junta todos os valores separados por vírgula


    cv2.imshow("Hand Tracking", frame) # abre uma janela chamada "Hand Tracking" e mostra o frame da webcam
    if cv2.waitKey(1) & 0xFF == ord('q'): # q serve para fechar a webcam poder ser trocando por outra tecla
        break

cap.release() # libera a webcam para outros programas.
cv2.destroyAllWindows() # fecha todas as janelas abertas pelo OpenCV.
```
## Código Arduino💻
```
#include <Servo.h> // biblioteca para controlar os servos motores

Servo servos[5]; //vetor servos para guarda 
int angles[5]; // vetor para guarda os angulos dos servos(dedos) que sao recebidos pela ponta serial

void setup() {
  // aqui atraves de .attach conectar cada servo a um pino digital 
  Serial.begin(9600);
  servos[0].attach(3);  // polegar
  servos[1].attach(5);  // indicador
  servos[2].attach(6);  // médio
  servos[3].attach(9);  // anelar
  servos[4].attach(10); // mínimo
}

void loop() {
  if (Serial.available()) {//so executa ser algo for enviado
    String data = Serial.readStringUntil('\n');//pega tudo até encontrar um Enter
    int i = 0;
    char *token = strtok((char*)data.c_str(), ","); //separa a string em pedaços usando a vírgula como delimitador.
    while (token != NULL && i < 5) {
      angles[i] = atoi(token);// atoi transforma texto em número inteiro
      servos[i].write(angles[i]); //  move o servo para o ângulo correspondente
      token = strtok(NULL, ",");  // aqui ela vai pegando o próximo pedaço até não encontrar mais vírgulas (quando retorna NULL).
      i++;
    }
  }
}
```
