import socket
import re
import time
from typing import List, Dict

import cv2
import numpy as np
import numpy.typing as npt

from is_msgs.image_pb2 import Image

from is_wire.core import Channel, Message, Subscription
from is_wire.core.utils import now


class CustomChannel(Channel):
    def __init__(
        self,
        uri: str = "amqp://guest:guest@localhost:5672",
        exchange: str = "is",
    ) -> None:
        super().__init__(uri=uri, exchange=exchange)
        self._deadline = now()
        self._running = False

    def consume_for(self, period: float) -> List[Message]:
        if not self._running:
            self._deadline = now()
            self._running = True
        self._deadline = self._deadline + period
        messages = []
        while True:
            try:
                message = self.consume_until(deadline=self._deadline)
                messages.append(message)
            except socket.timeout:
                break
        return messages

    def consume_until(self, deadline: float) -> Message:
        timeout = max([deadline - now(), 0.0])
        return self.consume(timeout=timeout)


class App(object):
    def __init__(
        self,
        cameras: List[int] = [0, 1, 2, 3], # Id das câmeras que serão mostradas
        broker_uri: str = "amqp://guest:guest@localhost:5672",
    ) -> None:
        self.channel = CustomChannel(uri=broker_uri, exchange="is")
        self.subscription = Subscription(channel=self.channel, name="app")
        for camera in cameras:
            self.subscription.subscribe(f"CameraGateway.{camera}.Frame")

    @staticmethod
    def to_np(image: Image) -> npt.NDArray[np.uint8]:
        buffer = np.frombuffer(image.data, dtype=np.uint8)
        output = cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
        return output

    @staticmethod
    def get_topic_id(topic: str) -> str:
        re_topic = re.compile(r"CameraGateway.(\d+).Frame")
        result = re_topic.match(topic)
        if result:
            return result.group(1)

    def stack_images(self, images_dict):
        cam_ids = sorted(images_dict.keys(), key=int)
        images = [images_dict[cam_id] for cam_id in cam_ids]
        stacked_img = np.hstack(images)
        return stacked_img

    def run(self) -> None:
        fps = 0
        count = 0
        while True:
            ti = time.perf_counter()
            messages = self.channel.consume_for(period=0.1)
            images: Dict[int, npt.NDArray[np.uint8]] = {}
            for message in messages:
                camera_id = self.get_topic_id(message.topic)
                image = self.to_np(message.unpack(Image))
                images[camera_id] = image
            print(images.keys())
            if len(images) > 0:

                stack_image = self.stack_images(images)
                cv2.namedWindow("stacked images", cv2.WINDOW_KEEPRATIO)
                cv2.imshow("stacked images", stack_image)
                key = cv2.waitKey(1)


                images.clear()
            tf = time.perf_counter()
            fps += 1/(tf - ti)
            count += 1
            if count >= 20:
                print(f"FPS : {fps/20}")
                count = 0
                fps = 0


if __name__ == "__main__":
    app = App(broker_uri="amqp://guest:guest@localhost:5672")
    app.run()
