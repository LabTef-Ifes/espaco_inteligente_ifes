import os
import re
import sys
import csv
import cv
import cv2
import json
import time
import argparse
import numpy as np
import math
import statistics
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from is_wire.core import Logger
from utils import load_options, to_labels_array, to_labels_dict, get_np_image

from video_loader import MultipleVideoLoader
from is_wire.core import Logger
from collections import defaultdict, OrderedDict
from is_msgs.image_pb2 import ObjectAnnotations

"""_summary_
"""
log = Logger(name='WatchVideos')

with open('keymap.json', 'r') as f:
    keymap = json.load(f)
options = load_options(print_options=False)

FPS = 21.0

# Why do VideoCapture in this py file?
for i in range(4):
    cap = cv2.VideoCapture(
        options.folder+'TESTE_GRAYSCALE/TESTE_GRAYSCALE_6/p001g01c{:02d}.mp4'.format(i))
    #cap.set(cv2.CAP_PROP_FORMAT, CV_32F)
    ret, frame = cap.read()
    #print('ret =', ret, 'W =', frame.shape[1], 'H =', frame.shape[0], 'channel =', frame.shape[2])

    FrameSize = (frame.shape[1], frame.shape[0])
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_video = str(
        options.folder+'TESTE_GRAYSCALE/21_fps_teste/p001g01c{:02d}.mp4'.format(i))
    out = cv2.VideoWriter(out_video, fourcc, FPS, FrameSize)

    while(cap.isOpened()):
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
