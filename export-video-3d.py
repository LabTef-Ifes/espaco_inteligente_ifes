import os
import re
import sys
import cv2
import json
import time
import argparse
import numpy as np
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

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import pyscreenshot as ImageGrab

colors = list(permutations([0, 255, 85, 170], 3))
links = [(HKP.Value('HEAD'), HKP.Value('NECK')), (HKP.Value('NECK'), HKP.Value('CHEST')),
         (HKP.Value('CHEST'), HKP.Value('RIGHT_HIP')), (HKP.Value('CHEST'), HKP.Value('LEFT_HIP')),
         (HKP.Value('NECK'), HKP.Value('LEFT_SHOULDER')),
         (HKP.Value('LEFT_SHOULDER'), HKP.Value('LEFT_ELBOW')),
         (HKP.Value('LEFT_ELBOW'), HKP.Value('LEFT_WRIST')),
         (HKP.Value('NECK'), HKP.Value('LEFT_HIP')), (HKP.Value('LEFT_HIP'),
                                                      HKP.Value('LEFT_KNEE')),
         (HKP.Value('LEFT_KNEE'), HKP.Value('LEFT_ANKLE')),
         (HKP.Value('NECK'), HKP.Value('RIGHT_SHOULDER')),
         (HKP.Value('RIGHT_SHOULDER'), HKP.Value('RIGHT_ELBOW')),
         (HKP.Value('RIGHT_ELBOW'), HKP.Value('RIGHT_WRIST')),
         (HKP.Value('NECK'), HKP.Value('RIGHT_HIP')),   
         (HKP.Value('RIGHT_HIP'), HKP.Value('RIGHT_KNEE')),
         (HKP.Value('RIGHT_KNEE'), HKP.Value('RIGHT_ANKLE')),
         (HKP.Value('NOSE'), HKP.Value('LEFT_EYE')), (HKP.Value('LEFT_EYE'),
                                                      HKP.Value('LEFT_EAR')),
         (HKP.Value('NOSE'), HKP.Value('RIGHT_EYE')),
         (HKP.Value('RIGHT_EYE'), HKP.Value('RIGHT_EAR'))]


def render_skeletons(images, annotations, it, links, colors):
    for cam_id, image in images.items():
        deteccoes = 0 # Detections in each frame
        skeletons = ParseDict(annotations[cam_id][it], ObjectAnnotations())
        for ob in skeletons.objects:
            parts = {}
            for part in ob.keypoints:
                deteccoes += 1
                juntas[cam_id] += 1
                parts[part.id] = (int(part.position.x), int(part.position.y))
            for link_parts, color in zip(links, colors):
                begin, end = link_parts
                if begin in parts and end in parts:
                    cv2.line(image, parts[begin], parts[end], color=color, thickness=4)
            for _, center in parts.items():
                cv2.circle(image, center=center, radius=4, color=(255, 255, 255), thickness=-1)

        if deteccoes < 10:
            juntas[cam_id] -= deteccoes    
            # perdidas[cam_id] = 0
        else:
            perdidas[cam_id] += 15 - deteccoes
    
    return juntas, perdidas
        


def render_skeletons_3d(ax, skeletons, links, colors, juntas_3d, perdidas_3d):
    deteccoes_3d = 0
    skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
    for skeleton in skeletons_pb.objects:
        parts = {}
        for part in skeleton.keypoints:
            deteccoes_3d += 1
            juntas_3d += 1 
            parts[part.id] = (part.position.x, part.position.y, part.position.z)
        for link_parts, color in zip(links, colors):
            begin, end = link_parts
            if begin in parts and end in parts:
                x_pair = [parts[begin][0], parts[end][0]]
                y_pair = [parts[begin][1], parts[end][1]]
                z_pair = [parts[begin][2], parts[end][2]]
                ax.plot(
                    x_pair,
                    y_pair,
                    zs=z_pair,
                    linewidth=3,
                    color='#{:02X}{:02X}{:02X}'.format(*reversed(color)))
    
    if deteccoes_3d < 10:
        juntas_3d -= deteccoes_3d
    else:
        perdidas_3d += 15 - deteccoes_3d
    return juntas_3d, perdidas_3d


def perdas_3d(ax, skeletons, links, colors):
    skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
    for skeleton in skeletons_pb.objects:
        parts = {}
        for part in skeleton.keypoints:
            parts[part.id] = (part.position.x, part.position.y, part.position.z)
        for link_parts, color in zip(links, colors):
            begin, end = link_parts
            if begin in parts and end in parts:
                x_pair = [parts[begin][0], parts[end][0]]
                y_pair = [parts[begin][1], parts[end][1]]
                z_pair = [parts[begin][2], parts[end][2]]
                perdas=(15-len(parts))/15.0
                perdas=perdas*100.0
                #print("Perdas na detecção: " +   str(perdas) + "%")
                return perdas

def place_images(output_image, images, x_offset=0, y_offset=0):
    w, h = images[0].shape[1], images[0].shape[0]
    output_image[0 + y_offset:h + y_offset, 0 + x_offset:w + x_offset, :] = images[0]
    output_image[0 + y_offset:h + y_offset, w + x_offset:2 * w + x_offset, :] = images[1]
    output_image[h + y_offset:2 * h + y_offset, 0 + x_offset:w + x_offset, :] = images[2]
    output_image[h + y_offset:2 * h + y_offset, w + x_offset:2 * w + x_offset, :] = images[3]

def plota_grafico_perdas(x,y):
    fig2,AX=plt.subplots()
    AX.plot(x,y)
    AX.set(xlabel='Medição',ylabel='Perda percentual (%)',title='Perdas na reconstrução 3D em função da amostragem')
    AX.grid()
    plt.show()

log = Logger(name='WatchVideos')
with open('keymap.json', 'r') as f:
    keymap = json.load(f)
options = load_options(print_options=False)

if not os.path.exists(options.folder):
    log.critical("Folder '{}' doesn't exist", options.folder)

with open('gestures.json', 'r') as f:
    gestures = json.load(f)
    gestures = OrderedDict(sorted(gestures.items(), key=lambda kv: int(kv[0])))

parser = argparse.ArgumentParser(
    description='Utility to capture a sequence of images from multiples cameras')
parser.add_argument('--person', '-p', type=int, required=True, help='ID to identity person')
parser.add_argument('--gesture', '-g', type=int, required=True, help='ID to identity gesture')
args = parser.parse_args()

person_id = args.person
gesture_id = args.gesture
if str(gesture_id) not in gestures:
    log.critical("Invalid GESTURE_ID: {}. \nAvailable gestures: {}", gesture_id,
                 json.dumps(gestures, indent=2))

if person_id < 1 or person_id > 999:
    log.critical("Invalid PERSON_ID: {}. Must be between 1 and 999.", person_id)

log.info("PERSON_ID: {} GESTURE_ID: {}", person_id, gesture_id)

cameras = [int(cam_config.id) for cam_config in options.cameras]
video_files = {
    cam_id: os.path.join(options.folder, 'p{:03d}g{:02d}c{:02d}.mp4'.format(
        person_id, gesture_id, cam_id))
    for cam_id in cameras
}
json_files = {
    cam_id: os.path.join(options.folder, 'p{:03d}g{:02d}c{:02d}_2d.json'.format(
        person_id, gesture_id, cam_id))
    for cam_id in cameras
}
json_locaizations_file = os.path.join(options.folder, 'p{:03d}g{:02d}_3d.json'.format(
    person_id, gesture_id))

if not all(
        map(os.path.exists,
            list(video_files.values()) + list(json_files.values()) + [json_locaizations_file])):
    log.critical('Missing one of video or annotations files from PERSON_ID {} and GESTURE_ID {}',
                 person_id, gesture_id)

size = (2 * options.cameras[0].config.image.resolution.height,
        2 * options.cameras[0].config.image.resolution.width, 3)
full_image = np.zeros(size, dtype=np.uint8)

video_loader = MultipleVideoLoader(video_files)
# load annotations
annotations = {}
for cam_id, filename in json_files.items():
    with open(filename, 'r') as f:
        annotations[cam_id] = json.load(f)['annotations']
#load localizations
with open(json_locaizations_file, 'r') as f:
    localizations = json.load(f)['localizations']

plt.ioff()
fig = plt.figure(figsize=(5, 5))
ax = Axes3D(fig)

update_image = True
output_file = 'p{:03d}g{:02d}_output.mp4'.format(person_id, gesture_id)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
vid = cv2.VideoWriter('record_screen.avi', fourcc, 60.0, (1288,728))
# video_writer = cv2.VideoWriter()

juntas = [0, 0, 0, 0]           # Lista de juntas detectadas em cada câmera
perdidas = [0, 0, 0, 0]         # Lista de juntas perdidas em cada câmera
juntas_3d = 0
perdidas_3d = 0
it_frames = 0
y = []
x = []
i=0
tempo_inicial=time.time()
for it_frames in range(video_loader.n_frames()):
    video_loader.load_next()

    frames = video_loader[it_frames]
    if frames is not None:

        juntas, perdidas = render_skeletons(frames, annotations, it_frames, links, colors)
        frames_list = [frames[cam] for cam in sorted(frames.keys())]
        place_images(full_image, frames_list)

    ax.clear()
    ax.view_init(azim=28, elev=32)
    ax.set_xlim(-1.5, 0)
    ax.set_xticks(np.arange(-1.5, 0.5, 0.5))
    ax.set_ylim(-3.0, 3.0)
    ax.set_yticks(np.arange(-5.0, 2.0, 0.5))
    ax.set_zlim(-0.25, 1.5)
    ax.set_zticks(np.arange(0, 1.75, 0.5))
    ax.set_xlabel('X', labelpad=20)
    ax.set_ylabel('Y', labelpad=10)
    ax.set_zlabel('Z', labelpad=5)
    juntas_3d, perdidas_3d = render_skeletons_3d(ax, localizations[it_frames], links, colors, juntas_3d, perdidas_3d)
    i=1+i
    perdas_no_3d=perdas_3d(ax, localizations[it_frames], links, colors)
        
    if perdas_no_3d is None:
        perdas_no_3d=100

    y.append(perdas_no_3d)
    x.append(i) 
        
    print("Perdas no 3D: %5.2f"  % perdas_no_3d + "%")
    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    view_3d = data.reshape(fig.canvas.get_width_height()[::-1] + (3, ))

    display_image = cv2.resize(full_image, dsize=(0, 0), fx=0.5, fy=0.5)
    hd, wd, _ = display_image.shape
    hv, wv, _ = view_3d.shape

    display_image = np.hstack([display_image, 255 * np.ones(shape=(hd, wv, 3), dtype=np.uint8)])
    display_image[int((hd - hv) / 2):int((hd + hv) / 2), wd:, :] = view_3d

    # if it_frames == 0:
    #     video_writer.open(
    #         filename=output_file,
    #         fourcc=0x00000021,
    #         fps=10.0,
    #         frameSize=(display_image.shape[1], display_image.shape[0]))

    # video_writer.write(display_image)
    cv2.imshow('', display_image)

    # image = np.array(ImageGrab.grab())
    # image = get_np_image(image)
    # image = np.array(cv2.grab())
    # image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # cv2.imshow('', image)
    vid.write(display_image)
    # key = cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

for cam_id in range(0, 4):
    porcentagem = (perdidas[cam_id]/juntas[cam_id]) * 100
    log.info("cam{}: Juntas detectadas: {} | Perdidas: {} |  {:.2f} %".format(cam_id, juntas[cam_id], perdidas[cam_id], porcentagem))

porcentagem_3d = (perdidas_3d/juntas_3d) * 100
log.info("Juntas detectadas [Serviço 3d]: {} | Perdidas: {} |  {:.2f} %".format(juntas_3d, perdidas_3d, porcentagem_3d))

log.info('Exiting')
soma_perdas=sum(y)
tempo_final=time.time()
tempo_total=(tempo_final-tempo_inicial)
print("Tempo total: %5.4f" % tempo_total)
perda_media=soma_perdas/len(x)
print("Perda média: %5.2f" % perda_media + " %")
plota_grafico_perdas(x,y) 

vid.release()
cv2.destroyAllWindows()