import os
import re
import cv2
import json
import numpy as np
import matplotlib.pyplot as plt
from is_wire.core import Logger
from utils import load_options

from is_wire.core import Logger

"""_summary_
"""
FPS = 21
log = Logger(name='WatchVideos')

with open('keymap.json', 'r') as f:
    keymap = json.load(f)
options = load_options(print_options=False)

# Why do VideoCapture in this py file?
for i in range(4):
    cap = cv2.VideoCapture(
        options.folder + 'TESTE_GRAYSCALE/TESTE_GRAYSCALE_6/p001g01c{:02d}.mp4'.format(i))
    # cap.set(cv2.CAP_PROP_FORMAT, CV_32F)
    ret, frame = cap.read()

    FrameSize = (frame.shape[1], frame.shape[0])
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_video = str(
        options.folder + 'TESTE_GRAYSCALE/21_fps_teste/p001g01c{:02d}.mp4'.format(i))
    out = cv2.VideoWriter(out_video, fourcc, FPS, FrameSize)

    while cap.isOpened():
        ret, frame = cap.read()
        # check for successfulness of cap.read()
        if not ret:
            break

        # Save the frame
        out.write(frame)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
