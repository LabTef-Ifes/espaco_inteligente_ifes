import os
import re
import cv2
import json
import numpy as np
import matplotlib.pyplot as plt
from is_wire.core import Logger
from utils import load_options

from is_wire.core import Logger
from collections import OrderedDict

"""_summary_
"""
log = Logger(name='WatchVideos')

with open('keymap.json', 'r') as f:
    keymap = json.load(f)
options = load_options(print_options=False)

FPS = 21

# Why do VideoCapture in this py file?
for i in range(4):
    cap = cv2.VideoCapture(
        options.folder + 'TESTE_GRAYSCALE/TESTE_GRAYSCALE_6/p001g01c{:02d}.mp4'.format(i))
    # cap.set(cv2.CAP_PROP_FORMAT, CV_32F)
    ret, frame = cap.read()
    # print('ret =', ret, 'W =', frame.shape[1], 'H =', frame.shape[0], 'channel =', frame.shape[2])

    FrameSize = (frame.shape[1], frame.shape[0])
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_video = str(
        options.folder + 'TESTE_GRAYSCALE/21_fps_teste/p001g01c{:02d}.mp4'.format(i))
    out = cv2.VideoWriter(out_video, fourcc, FPS, FrameSize)

    while cap.isOpened():
        ret, frame = cap.read()
        # print(frame.shape)
        # check for successfulness of cap.read()
        if not ret:
            break

        # frame=cv2.merge([frame])
        # frame = cv2.cvtColor(frame,  cv2.COLOR_GRAY2BGR)
        # frame=cv2.merge([frame])
        # frame = gray

        # Save the video
        out.write(frame)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
