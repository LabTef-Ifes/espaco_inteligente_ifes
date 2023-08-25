import asyncio
from is_wire.core import Channel, Subscription, Message
from is_msgs.image_pb2 import Image
import numpy as np
import cv2
import json
import time
from datetime import date, datetime
import os
import sys

# Recebe o id da camera como argumento da linha de comando ou usa o valor padrão
try:
    camera_id = sys.argv[1]
except:
    camera_id = 3

net = cv2.dnn.readNetFromTensorflow("graph_opt.pb")

mode = 1 # 0 auto, 1 manual

BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
               "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
               "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
               "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
               ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
               ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
               ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
               ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]

today = date.today()

parent_folder = f'calibration_img/extrinsic/' # Definir o path para salvar as imagens
path = os.path.join(parent_folder,f'cam{camera_id}/')
# Cria a pasta da camera se ela não existir
if not os.path.exists(path):
    os.makedirs(path)

print('path',path)

def to_np(input_image):
    if isinstance(input_image, np.ndarray):
        return input_image
    elif isinstance(input_image, Image):
        buffer = np.frombuffer(input_image.data, dtype=np.uint8)
        return cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    else:
        return np.array([], dtype=np.uint8)

def cnn(im):
    frame = to_np(im)
    start = time.time()
    net.setInput(cv2.dnn.blobFromImage(frame, 1.0, (1440, 1080), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    print(time.time()-start)
    out = net.forward()
    out = out[:, :19, :, :]  # MobileNet output [1, 57, -1, -1], we only need the first 19 elements


    points = []
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponging body's part.
        heatMap = out[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv2.minMaxLoc(heatMap)
        x = (1440 * point[0]) / out.shape[3]
        y = (1080 * point[1]) / out.shape[2]
        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > .5 else None)

    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv2.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv2.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv2.FILLED)
            cv2.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv2.FILLED)

    t, _ = net.getPerfProfile()
    freq = cv2.getTickFrequency() / 1000

    return frame, t, freq
if __name__ == '__main__':

    print('---RUNNING EXAMPLE DEMO OF THE CAMERA CLIENT---')

    broker_uri = "amqp://guest:guest@localhost:5672"
    channel = Channel(broker_uri)
    subscription = Subscription(channel=channel)
    subscription.subscribe(topic='CameraGateway.{}.Frame'.format(camera_id))

    window = 'Blackfly S Camera'

    n = 0
    start = time.time()
    cont = 0
    while True:
        cont +=1
        msg = channel.consume()
        im = msg.unpack(Image)
        
        frame, t, freq = cnn(im)
        #frame = to_np(im)

        #cv2.putText(frame, '%.2fms' % (t / freq), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
        cv2.imshow(window, frame)

        key = cv2.waitKey(1)

        # Stops the recording
        if key == ord('q'):
            break

        # Saves the frame on pressing 's'
        if key == ord('s'):

            n += 1
            print(f'imagem {n} salva')
            cv2.imwrite(
                f'{path}data_{today}_camera{camera_id}_{n:0>3}.png', frame)
        if mode == 0 and cont%5 == 0:
            cont = 0
            n += 1
            print(f'imagem {n} salva')
            cv2.imwrite(
                f'{path}data_{today}_camera{camera_id}_{n:0>3}.png', frame)