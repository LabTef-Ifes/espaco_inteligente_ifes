import os
import re
import sys
import cv2
import json
import time
import argparse
import numpy as np
import time
from utils import load_options
from utils import to_labels_array, to_labels_dict
from video_loader import MultipleVideoLoader
from is_wire.core import Logger
from collections import defaultdict, OrderedDict

from is_msgs.image_pb2 import ObjectAnnotations
from is_msgs.image_pb2 import HumanKeypoints as HKP
from google.protobuf.json_format import ParseDict
from itertools import permutations

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

        if deteccoes < 14:
            juntas[cam_id] -= deteccoes    
            perdidas[cam_id] = 0
        else:
            perdidas[cam_id] += 15 - deteccoes
    
    return juntas, perdidas
        
def step_length():
    if len(posicao_inicial) == 0:
        sdfsfsd
    if len(posicao_final) == 0:
        sdfsdfsd
    if pe_id == 0:
        adfsdfds
    
def left_leg(skeletons):
    skeletons_pb = ParseDict( skeletons, ObjectAnnotations())
    for skeletons in skeletons_pb.objects:
        parts = {}
        for part in skeletons.keypoints:
            parts[part.id]=(part.position.x,part.position.y,part.position.z)

        left_hip=parts[13]
        left_knee=parts[14]
        left_ankle=parts[15]
        a=np.sqrt((left_ankle[0]-left_knee[0])**2+(left_ankle[1]-left_knee[1])**2+(left_ankle[2]-left_knee[2])**2)
        b=np.sqrt((left_knee[0]-left_hip[0])**2 +(left_knee[1]-left_hip[1])**2 +(left_knee[2]-left_hip[2])**2)
        left_leg=a+b
        break
    return left_leg

def right_leg(skeletons):
    skeletons_pb = ParseDict( skeletons, ObjectAnnotations())
    for skeletons in skeletons_pb.objects:
        parts = {}
        for part in skeletons.keypoints:
            parts[part.id]=(part.position.x,part.position.y,part.position.z)

        right_hip=parts[10]
        right_knee=parts[11]
        right_ankle=parts[12]
        a=np.sqrt((right_ankle[0]-right_knee[0])**2+(right_ankle[1]-right_knee[1])**2+(right_ankle[2]-right_knee[2])**2)
        b=np.sqrt((right_knee[0]-right_hip[0])**2 +(right_knee[1]-right_hip[1])**2 +(right_knee[2]-right_hip[2])**2)
        right_leg=a+b
        break
    return right_leg


def render_skeletons_3d(ax, skeletons, links, colors, posicao_inicial, final_passo, pe_id, pe_direito, pe_esquerdo, posicao_final):
    skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
    comprimento_passo=0
    for skeleton in skeletons_pb.objects:
        parts = {}
        for part in skeleton.keypoints:
            parts[part.id] = (part.position.x, part.position.y, part.position.z)
            if part.id == 15:
                pe_direito = parts[15]
            if part.id == 12:
                pe_esquerdo = parts[12]
        
        print("Pos pé direito: {} | Pos pé esquerdo: {}".format(pe_direito, pe_esquerdo))
        # print("posicao inicial: {}".format(posicao_inicial))
        
        if pe_esquerdo[2] < 0.145 and pe_direito[2] >= 0.145:
            posicao_inicial = pe_esquerdo
            final_passo = False
            pe_id = 12
        
        if pe_direito[2] < 0.145 and pe_esquerdo[2] >= 0.145:
            posicao_inicial = pe_direito
            final_passo = False
            pe_id = 15

        if pe_direito[2] < 0.145 and pe_esquerdo[2] < 0.145:
            if pe_id == 12:
                posicao_final = pe_direito
                final_passo = True
                pe_id = 15
            elif pe_id == 15:
                posicao_final = pe_esquerdo
                final_passo = True
                pe_id = 12
            else:
                posicao_inicial = pe_esquerdo
        if final_passo:
            comprimento_passo = abs(np.sqrt((posicao_final[0] - posicao_inicial[0])**2 + (posicao_final[1] - posicao_inicial[1])**2))
            posicao_inicial = posicao_final
        else:
            comprimento_passo = 0
            posicao_final = ()

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
    return posicao_inicial, posicao_final, final_passo, comprimento_passo, pe_id, pe_direito, pe_esquerdo, posicao_final

def place_images(output_image, images, x_offset=0, y_offset=0):
    w, h = images[0].shape[1], images[0].shape[0]
    output_image[0 + y_offset:h + y_offset, 0 + x_offset:w + x_offset, :] = images[0]
    output_image[0 + y_offset:h + y_offset, w + x_offset:2 * w + x_offset, :] = images[1]
    output_image[h + y_offset:2 * h + y_offset, 0 + x_offset:w + x_offset, :] = images[2]
    output_image[h + y_offset:2 * h + y_offset, w + x_offset:2 * w + x_offset, :] = images[3]


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

erro_cameras = []
juntas = [0, 0, 0, 0]           # Lista de juntas detectadas em cada câmera
perdidas = [0, 0, 0, 0]         # Lista de juntas perdidas em cada câmera
pe_direito = ()
pe_esquerdo = ()
final_passo = False
posicao_inicial = ()
posicao_final = ()
pe_id = 0
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
    ax.set_xlim(-1.5, 1.5)
    ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks(np.arange(-1.5, 2.0, 0.5))
    ax.set_zlim(-0.25, 1.5)
    ax.set_zticks(np.arange(0, 1.75, 0.5))
    ax.set_xlabel('X', labelpad=20)
    ax.set_ylabel('Y', labelpad=10)
    ax.set_zlabel('Z', labelpad=5)
    # render_skeletons_3d(ax, localizations[it_frames], links, colors)
    posicao_inicial, posicao_final, final_passo, comprimento_passo, pe_id, pe_direito, pe_esquerdo, posicao_final = render_skeletons_3d(
        ax, localizations[it_frames], links, colors, posicao_inicial, final_passo, pe_id, pe_direito, pe_esquerdo, posicao_final
    )
    perna_esquerda=left_leg(localizations[it_frames])
    print("Tamanho do perna esquerda: %5.3f m" % perna_esquerda)
    perna_direita=right_leg(localizations[it_frames])
    print("Tamanho do perna direita: %5.3f m" % perna_direita)

    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    view_3d = data.reshape(fig.canvas.get_width_height()[::-1] + (3, ))

    display_image = cv2.resize(full_image, dsize=(0, 0), fx=0.5, fy=0.5)
    hd, wd, _ = display_image.shape
    hv, wv, _ = view_3d.shape

    display_image = np.hstack([display_image, 255 * np.ones(shape=(hd, wv, 3), dtype=np.uint8)])
    display_image[int((hd - hv) / 2):int((hd + hv) / 2), wd:, :] = view_3d

    cv2.imshow('', display_image)
    key = cv2.waitKey(500)
    if key == ord("p"):
        input("")
    
    # if comprimento_passo > 0:
    log.info("Comprimento de passo: {}".format(comprimento_passo))

for cam_id in range(0, 4):
    porcentagem = (perdidas[cam_id]/juntas[cam_id]) * 100
    log.info("cam{}: Juntas detectadas: {} | Perdidas: {} |  {:.2f} %".format(cam_id, juntas[cam_id], perdidas[cam_id], porcentagem))

tempo_final=time.time()
log.info("Comprimento de passo: {}".format(comprimento_passo))
tempo_duplo_suporte=0.2*(tempo_final-tempo_inicial)
log.info("Tempo de duplo suporte: " + str(tempo_duplo_suporte))
log.info('Exiting')
