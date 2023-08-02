from is_wire.core import Channel, Subscription, Message
from is_msgs.image_pb2 import Image
import numpy as np
import cv2
import json
import time


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

    print('---RUNNING EXAMPLE DEMO OF THE CAMERA CLIENT---')

    broker_uri = "amqp://guest:guest@localhost:5672"
    camera_id = 3
    channel = Channel(broker_uri)
    subscription = Subscription(channel=channel)
    subscription.subscribe(topic='CameraGateway.{}.Frame'.format(camera_id))

    print(channel)

    window = 'Blackfly S Camera'

    while True:
        msg = channel.consume()
        im = msg.unpack(Image)
        frame = to_np(im)
        # print(frame.shape)
        cv2.imshow(window, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
