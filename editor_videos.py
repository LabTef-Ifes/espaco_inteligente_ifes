import os
import re
import sys
import cv2
import json
import time
import argparse
import numpy as np
import math
import statistics
from moviepy.editor import *
from utils import load_options
from utils import to_labels_array, to_labels_dict
from video_loader import MultipleVideoLoader
from is_wire.core import Logger
from collections import defaultdict, OrderedDict
from utils import get_np_image
#from PIL import ImageGrab
from is_msgs.image_pb2 import ObjectAnnotations
from is_msgs.image_pb2 import HumanKeypoints as HKP
from google.protobuf.json_format import ParseDict
from itertools import permutations

log = Logger(name='WatchVideos')
with open('keymap.json', 'r') as f:
    keymap = json.load(f)
options = load_options(print_options=False)


from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# ffmpeg_extract_subclip("full.mp4", start_seconds, end_seconds, targetname="cut.mp4")
k=18
for i in range(0,4):
#    ffmpeg_extract_subclip(options.folder+"/p001g01c{:02d}.mp4".format(i), 11, 22, targetname=options.folder+"/{:02d}_{:02d}.mp4".format(k,i))
    video = VideoFileClip(options.folder+"/p001g01c{:02d}.mp4".format(i))
    cortado = video.subclip(1,9)
    cortado.write_videofile(options.folder+"/{:02d}_{:02d}.mp4".format(k,i))
k=k+1
for i in range(0,4):
#    ffmpeg_extract_subclip(options.folder+"/p001g01c{:02d}.mp4".format(i), 11, 22, targetname=options.folder+"/{:02d}_{:02d}.mp4".format(k,i))
    video = VideoFileClip(options.folder+"/p001g01c{:02d}.mp4".format(i))
    cortado = video.subclip(14, 21)
    cortado.write_videofile(options.folder+"/{:02d}_{:02d}.mp4".format(k,i))
k=k+1
for i in range(0,4):
#    ffmpeg_extract_subclip(options.folder+"/p001g01c{:02d}.mp4".format(i), 11, 22, targetname=options.folder+"/{:02d}_{:02d}.mp4".format(k,i))
    video = VideoFileClip(options.folder+"/p001g01c{:02d}.mp4".format(i))
    cortado = video.subclip(20, 26)
    cortado.write_videofile(options.folder+"/{:02d}_{:02d}.mp4".format(k,i))
k=k+1
for i in range(0,4):
#    ffmpeg_extract_subclip(options.folder+"/p001g01c{:02d}.mp4".format(i), 11, 22, targetname=options.folder+"/{:02d}_{:02d}.mp4".format(k,i))
    video = VideoFileClip(options.folder+"/p001g01c{:02d}.mp4".format(i))
    cortado = video.subclip(26, 31)
    cortado.write_videofile(options.folder+"/{:02d}_{:02d}.mp4".format(k,i))
k=k+1
for i in range(0,4):
#    ffmpeg_extract_subclip(options.folder+"/p001g01c{:02d}.mp4".format(i), 11, 22, targetname=options.folder+"/{:02d}_{:02d}.mp4".format(k,i))
    video = VideoFileClip(options.folder+"/p001g01c{:02d}.mp4".format(i))
    cortado = video.subclip(29,36)
    cortado.write_videofile(options.folder+"/{:02d}_{:02d}.mp4".format(k,i))