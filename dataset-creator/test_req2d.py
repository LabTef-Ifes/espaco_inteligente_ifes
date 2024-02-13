import os
import time
import socket

import cv2
import numpy as np
import numpy.typing as npt

from google.protobuf.json_format import MessageToJson
from is_msgs.image_pb2 import Image, ObjectAnnotations
from is_wire.core import Channel, Message, Subscription


def array2image(
    image: npt.NDArray[np.uint8],
    encode_format: str = ".jpeg",
    compression_level: float = 0.8,
) -> Image:
    if encode_format == ".jpeg":
        params = [cv2.IMWRITE_JPEG_QUALITY, int(compression_level * (100 - 0) + 0)]
    elif encode_format == ".png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, int(compression_level * (9 - 0) + 0)]
    else:
        return Image()
    cimage = cv2.imencode(ext=encode_format, img=image, params=params)
    return Image(data=cimage[1].tobytes())

def main(amqp_address='amqp://guest:guest@localhost:5672') -> None:
    channel = Channel(amqp_address)
    subscription = Subscription(channel)

    # Prepare request
    array = cv2.imread("test.jpg")
    image = array2image(image=array)
    request = Message(content=image, reply_to=subscription)
    # Make request
    ti = time.time()
    channel.publish(request, topic="SkeletonsDetector.Detect")

    # Wait for reply with 1.0 seconds timeout
    try:
        reply = channel.consume(timeout=0.5)
        tf = time.time()
        print((tf - ti)*1000)
        annotations = reply.unpack(ObjectAnnotations)
        print('RPC Status:', reply.status, '\nReply:', annotations)
        with open(
            file="data.json",
            mode="w",
            encoding="utf-8",
        ) as file:
            content = MessageToJson(annotations, indent=2)
            file.write(content)
    except socket.timeout:
        print('No reply :(')

    

if __name__ == "__main__":
    main()