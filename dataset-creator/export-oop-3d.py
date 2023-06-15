import os
import re
import sys
import cv2
import json
import time
import argparse
import numpy as np
from utils import to_labels_array, to_labels_dict,load_options
from video_loader import MultipleVideoLoader
from is_wire.core import Logger
from collections import defaultdict, OrderedDict
from is_msgs.image_pb2 import HumanKeypoints as HKP,ObjectAnnotations
from google.protobuf.json_format import ParseDict
from itertools import permutations
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
JSON2D_FORMAT = 'p{:03d}g{:02d}c{:02d}_2d.json'
JSON3D_FORMAT = 'p{:03d}g{:02d}_3d.json'
FOURCC = cv2.VideoWriter_fourcc(*"XVID")

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


class Export:
    OUTPUT_FORMAT = 'p{:03d}g{:02d}_output.avi'

    def __init__(self):
        self.log = Logger(name='Export3D')
        plt.ioff()
        self.fig = plt.figure(figsize=(5, 5))
        self.ax:Axes3D = Axes3D(self.fig)

        self.person_id, self.gesture_id = self.get_person_gesture_parser()
        self.output_file = os.path.join(current_dir_path,'videos',self.OUTPUT_FORMAT.format(self.person_id, self.gesture_id))
        # corrigir W,H fixados
        self.video_writer = cv2.VideoWriter(self.output_file, FOURCC, 15, (1940, 1080))
        self.options = self.get_options()
        self.keymap = self.get_keymap()
        self.gestures = self.check_gesture(self.gesture_id)
    
        self.size = (2 * self.options.cameras[0].config.image.resolution.height,
                     2 * self.options.cameras[0].config.image.resolution.width,
                     3)
        self.full_image = np.zeros(self.size, dtype=np.uint8)
        
        self.cameras_id_list = [int(cam_config.id) for cam_config in self.options.cameras]

        self.video_files = {
            cam_id: os.path.join(self.options.folder, 'p{:03d}g{:02d}c{:02d}.mp4'.format(
                self.person_id, self.gesture_id, cam_id))
            for cam_id in self.cameras_id_list
        }

        self.json_files = {
            cam_id: os.path.join(self.options.folder, JSON2D_FORMAT.format(
                self.person_id, self.gesture_id, cam_id))
            for cam_id in self.cameras_id_list
        }

        self.json_localizations_file = os.path.join(self.options.folder, JSON3D_FORMAT.format(
            self.person_id, self.gesture_id))
        self.check_annotations_files()

        self.video_loader = MultipleVideoLoader(self.video_files)
        self.annotations = self.load_annotations()
        self.localizations = self.load_localizations()
    def get_keymap(self):
        with open('keymap.json', 'r') as f:
            keymap = json.load(f)
        return keymap
    
    def get_options(self):
        
        options = load_options(print_options=False)

        assert os.path.exists(options.folder),f"Folder '{options.folder}' doesn't exist"
        return options
    def get_person_gesture_parser(self):
        parser = argparse.ArgumentParser(
            description='Utility to capture a sequence of images from multiples cameras')
        parser.add_argument('--person', '-p', type=int, required=True, help='ID to identity person')
        parser.add_argument('--gesture', '-g', type=int, required=True, help='ID to identity gesture')
        args = parser.parse_args()
        person_id = args.person
        gesture_id = args.gesture
        return person_id, gesture_id


    def get_annotations(self):
        # load annotations
        annotations = {}
        for cam_id, filename in self.json_files.items():
            with open(filename, 'r') as f:
                annotations[cam_id] = json.load(f)['annotations']
        return annotations
    def get_localizations(self):
        with open(self.json_localizations_file, 'r') as f:
            localizations = json.load(f)['localizations']
        return localizations

    def check_gesture(self, gesture_id):
        with open('gestures.json', 'r') as f:
            gestures = json.load(f)
            gestures = OrderedDict(sorted(gestures.items(), key=lambda kv: int(kv[0])))

        if str(gesture_id) not in gestures:
            self.log.critical("Invalid GESTURE_ID: {}. \nAvailable gestures: {}", gesture_id,
                        json.dumps(gestures, indent=2))
            sys.exit(-1)
        return gestures
    def check_person(self, person_id,gesture_id):
        assert person_id < 1 or person_id > 999, f"Invalid PERSON_ID: {person_id}. Must be between 1 and 999."

        self.log.info("PERSON_ID: {} GESTURE_ID: {}", person_id, gesture_id)

    def check_annotations_files(self):
        if not all(
        map(os.path.exists,
            list(self.video_files.values()) + list(self.json_files.values()) + [self.json_localizations_file])):
            self.log.critical('Missing one of video or annotations files from PERSON_ID {} and GESTURE_ID {}',
                        self.person_id, self.gesture_id)
            sys.exit(-1)



    def run(self):
        for it_frames in range(video_loader.n_frames()):
            video_loader.load_next()

            frames = video_loader[it_frames]
            if frames is not None:
                render_skeletons(frames, annotations, it_frames, links, colors)
                frames_list = [frames[cam] for cam in sorted(frames.keys())]
                place_images(full_image, frames_list)

            # draw axis 3d
            ax.clear()
            ax.view_init(azim=28, elev=32)
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)
            ax.set_zlim(-0.25, 1.5)

            ax.set_xticks(np.arange(-1.5, 2.0, 0.5))
            ax.set_yticks(np.arange(-1.5, 2.0, 0.5))
            ax.set_zticks(np.arange(0, 1.75, 0.5))

            ax.set_xlabel('X', labelpad=20)
            ax.set_ylabel('Y', labelpad=10)
            ax.set_zlabel('Z', labelpad=5)

            render_skeletons_3d(ax, localizations[it_frames], links, colors)

            fig.canvas.draw()
            data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
            view_3d = data.copy().reshape(fig.canvas.get_width_height()[::-1] + (3, ))

            display_image = cv2.resize(full_image, dsize=(0, 0), fx=0.5, fy=0.5)
            hd, wd, _ = display_image.shape
            hv, wv, _ = view_3d.shape

            display_image = np.hstack([display_image, 255 * np.ones(shape=(hd, wv, 3), dtype=np.uint8)])
            display_image[int((hd - hv) / 2):int((hd + hv) / 2), wd:, :] = view_3d

            video_writer.write(display_image.astype(np.uint8))
            cv2.imshow('data', display_image)
            cv2.waitKey(1)

        video_writer.release()
        cv2.destroyAllWindows()
        log.info('Done!')
def render_skeletons(images:dict, annotations:dict, it, links:list, colors:list):
    for cam_id, image in images.items():
        skeletons = ParseDict(annotations[cam_id][it], ObjectAnnotations())
        for ob in skeletons.objects:
            parts = {}
            for part in ob.keypoints:
                parts[part.id] = (int(part.position.x), int(part.position.y))
            for link_parts, color in zip(links, colors):
                begin, end = link_parts
                if begin in parts and end in parts:
                    cv2.line(image, parts[begin], parts[end], color=color, thickness=4)
            for center in parts.values():
                cv2.circle(image, center=center, radius=4, color=(255, 255, 255), thickness=-1)


def render_skeletons_3d(ax, skeletons:dict, links:list, colors:list):
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
                ax.plot(
                    x_pair,
                    y_pair,
                    linewidth=3,
                    zs=z_pair,
                    color='#{:02X}{:02X}{:02X}'.format(*reversed(color)))


def place_images(output_image, images, x_offset=0, y_offset=0):
    w, h = images[0].shape[1], images[0].shape[0]
    output_image[0 + y_offset:h + y_offset, 0 + x_offset:w + x_offset, :] = images[0]
    output_image[0 + y_offset:h + y_offset, w + x_offset:2 * w + x_offset, :] = images[1]
    output_image[h + y_offset:2 * h + y_offset, 0 + x_offset:w + x_offset, :] = images[2]
    output_image[h + y_offset:2 * h + y_offset, w + x_offset:2 * w + x_offset, :] = images[3]

