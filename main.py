import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import serial

arduino = serial.Serial('COM8', 9600)

base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

HARD_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20)
]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    result = detector.detect(mp_image)

    if result.hand_landmarks:
        for hand_landmark in result.hand_landmarks:
            # --- desenha os pontos da mão ---
            h, w, _ = frame.shape
            for landmark in hand_landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

            for connection in HARD_CONNECTIONS:
                start = hand_landmark[connection[0]]
                end = hand_landmark[connection[1]]
                x1, y1 = int(start.x * w), int(start.y * h)
                x2, y2 = int(end.x * w), int(end.y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


            servo_angles = [] # lista vazia para guardar os ângulos de cada servo
            # que vai ser recebido abaixo

            # Polegar
            if hand_landmark[4].x < hand_landmark[2].x: # 4 ponta do polegar 2 base polegar
                servo_angles.append(150)  # fechado
            else:
                servo_angles.append(0)  # aberto

            # Indicador
            servo_angles.append(0 if hand_landmark[8].y < hand_landmark[6].y else 180) # 8 ponta do indicador 6 articulação do indicador.
            '''assim por diante'''
            # Médio
            servo_angles.append(0 if hand_landmark[12].y < hand_landmark[10].y else 180)
            # Anelar
            servo_angles.append(0 if hand_landmark[16].y < hand_landmark[14].y else 180)
            # Mínimo
            servo_angles.append(0 if hand_landmark[20].y < hand_landmark[18].y else 180)

            # envia para o Arduino
            arduino.write(f"{','.join(map(str, servo_angles))}\n".encode()) # aqui faz o envio para o arduino, map transforma cada número em string
            # junta todos os valores separados por vírgula
            #junta todos os valores separados por vírgula

    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): #aqui e para fecha a camera com a tecla q mais poder mudar
        break

cap.release() # aqui libera a câmera para que outros programas possam usar
cv2.destroyAllWindows() # fecha todas as janelas gráficas que o OpenCV abriu
