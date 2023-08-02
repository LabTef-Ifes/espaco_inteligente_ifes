# -*- coding: utf-8 -*-
import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from is_wire.core import Logger
from utils import load_options

"""Seleciona as imagens de todas as pastas "pXXXgXX" dentro da pasta `options.folder` e cria um vídeo de cada câmera para cada pasta com o nome "pXXXgXXcXX.mp4".
Pode ser executado com os argumentos -p e -g para gerar vídeos apenas para uma pessoa e gesto específicos.
"""


def get_person_gesture(folder):
    """gera uma tupla (person_id,gesture_id) a partir do nome da pasta

    Args:
        folder (str): nome da pasta que contém as fotos. Ex: p001g01

    Returns:
        Tuple[int]: (person_id,gesture_id). Ex :(1,1) for p001g01
    """
    match = re.search(r'p(\d+)g(\d+)', folder)
    if match is None:
        return None, None
    return int(match.group(1)), int(match.group(2))


def create_video(camera_id, file_pattern, video_file, fps):
    ffmpeg_base_command = "ffmpeg -y -r {fps:.1f} -start_number 0 -i {file_pattern:s} -c:v libx264 -vf fps={fps:.1f} -vf " \
                          "format=rgb24 {video_file:s} "

    ffmpeg_command = ffmpeg_base_command.format(
        fps=fps, file_pattern=file_pattern, video_file=video_file)
    process = subprocess.Popen(ffmpeg_command.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if process.wait() == 0:
        log.info("Done creating video '{}'".format(video_file))
    else:
        log.warn("\'{}\' failed".format(video_file))


if __name__ == "__main__":
    log = Logger(name='MakeVideos')
    options = load_options(print_options=False)
    parser = argparse.ArgumentParser(
        description='Utility to capture a sequence of images from multiples cameras')
    parser.add_argument('--person', '-p', type=int,
                        required=False, help='ID to identity person')
    parser.add_argument('--gesture', '-g', type=int,
                        required=False, help='ID to identity gesture')
    args = parser.parse_args()

    person_id_pre = args.person
    gesture_id_pre = args.gesture
    if not os.path.exists(options.folder):
        log.critical("Folder '{}' doesn't exist".format(options.folder))

    # Create a list to hold the tasks
    tasks = []

    for root, dirs, files in os.walk(options.folder):
        for exp_folder in dirs:
            person_id, gesture_id = get_person_gesture(exp_folder)
            if person_id is None or gesture_id is None:
                continue
            # Condição para executar apenas o pessoa e gesto desejados caso passe os argumentos -p e -g no terminal
            if (person_id_pre is not None and gesture_id_pre is not None) and not (person_id == person_id_pre and gesture_id == gesture_id_pre):
                continue

            sequence_folder = os.path.join(options.folder, exp_folder)
            for camera in options.cameras:
                file_pattern = os.path.join(
                    sequence_folder,
                    'c{camera_id:02d}s%08d.jpeg'.format(camera_id=camera.id))
                video_file = os.path.join(
                    options.folder, 'p{:03d}g{:02d}c{:02d}.mp4'.format(person_id, gesture_id, camera.id))
                if os.path.exists(video_file):
                    log.info("Video '{}' already exists".format(video_file))
                    continue
                # Submit the task to the thread pool
                tasks.append((camera.id, file_pattern, video_file,
                             camera.config.sampling.frequency.value))

        # only first folder level
        break

    # Create a thread pool with the number of desired workers (you can adjust this value to optimize performance)
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Start processing the tasks in parallel
        futures = [executor.submit(create_video, *task) for task in tasks]

        # Wait for all tasks to complete
        for future in as_completed(futures):
            # Get any exceptions raised during the task (if any)
            exc = future.exception()
            if exc is not None:
                log.error("Exception during video creation: {}".format(exc))
