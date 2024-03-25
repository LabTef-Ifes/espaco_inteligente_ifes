from ultralytics import YOLO
import matplotlib.pyplot as plt
# Load a model
from is_wire.core import Channel, Subscription, Message
from is_msgs.image_pb2 import Image
import numpy as np
import cv2
import torch

def to_np(input_image):
    if isinstance(input_image, np.ndarray):
        output_image = input_image
    elif isinstance(input_image, Image):
        buffer = np.frombuffer(input_image.data, dtype=np.uint8)
        output_image = cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    else:
        output_image = np.array([], dtype=np.uint8)
    return output_image


if __name__ == '__main__':
    
    model = YOLO('yolov8m-pose.pt')  # load an official model

    print('---RUNNING EXAMPLE DEMO OF THE CAMERA CLIENT---')

    broker_uri = "amqp://guest:guest@localhost:5672"
    camera_id = 0
    channel = Channel(broker_uri)
    subscription = Subscription(channel=channel)
    subscription.subscribe(topic='CameraGateway.{}.Frame'.format(camera_id))

    window = 'Blackfly S Camera'

    while True:
        print('consuming')
        msg = channel.consume()
        print('consumed')
        im = msg.unpack(Image)
        frame = to_np(im)
        results = model.predict(frame, show=True,conf=0.5,save=True,device=0)  # predict on an image
        # print(frame.shape)
        #cv2.imshow(window, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
