# -*- coding: utf-8 -*-
import re
import os
import sys
import json
import shutil
import argparse
from datetime import datetime as dt
from collections import defaultdict, OrderedDict
import cv2
import numpy as np
from utils import load_options
from is_msgs.image_pb2 import Image
from is_wire.core import Channel, Subscription, Message, Logger
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor,as_completed
"""_summary_
"""
# Iniciando o logger
log = Logger(name='capture-images')
# Carregando as opções de configuração
options = load_options(print_options=False)

def get_id(topic):
    """_summary_

    Args:
        topic (_type_): _description_

    Returns:
        _type_: _description_
    """
    match_id = re.compile(
        r'CameraGateway.(\d+).Frame')  # d significa digitos 0-9
    match = match_id.search(topic)
    if not match:
        return None
    return int(match.group(1))

def place_images(output_image, images_):
    """_summary_

    Args:
        output_image (_type_): _description_
        images_ (_type_): _description_
    """
    h, w = images_[0].shape[0:2]

    output_image[0:h, 0:w, :] = images_[0]
    output_image[0:h, w:2 * w, :] = images_[1]
    output_image[h:2 * h, 0:w, :] = images_[2]
    output_image[h:2 * h, w:2 * w, :] = images_[3]


def draw_info_bar(image, text, x, y,
                  background_color=(0, 0, 0),
                  text_color=(255, 255, 255),
                  draw_circle=False):
    """_summary_

    Args:
        image (_type_): _description_
        text (_type_): _description_
        x (_type_): _description_
        y (_type_): _description_
        background_color (tuple, optional): _description_. Defaults to (0, 0, 0).
        text_color (tuple, optional): _description_. Defaults to (255, 255, 255).
        draw_circle (bool, optional): _description_. Defaults to False.
    """
    fontFace = cv2.FONT_HERSHEY_DUPLEX
    fontScale = 1.0
    thickness = 1
    ((text_width, text_height), _) = cv2.getTextSize(
        text=text, fontFace=fontFace, fontScale=fontScale, thickness=thickness)

    cv2.rectangle(
        image,
        pt1=(0, y - text_height),
        pt2=(x + text_width, y),
        color=background_color,
        thickness=cv2.FILLED)

    if draw_circle:
        cv2.circle(
            image,
            center=(int(x / 2), int(y - text_height / 2)),
            radius=int(text_height / 3),
            color=(0, 0, 255),
            thickness=cv2.FILLED)

    cv2.putText(
        image,
        text=text,
        org=(x, y),
        fontFace=fontFace,
        fontScale=fontScale,
        color=text_color,
        thickness=thickness)


def get_gestures():
    """_summary_

    Returns:
        _type_: _description_
    """
    # Carregando o arquivo gestures.json com informações sobre gestos
    with open('gestures.json') as f:
        # Salvando os gestos em um dicionário ordenado pelos ids
        gestures = json.load(f)
        gestures = OrderedDict(sorted(gestures.items(), key=lambda kv: int(kv[0])))
    return gestures

def get_person_gesture_by_parser():
    """_summary_

    Returns:
        _type_: _description_
    """
    # Configurando argumentos para a linha de comando
    parser = argparse.ArgumentParser(
        description='Utility to capture a sequence of images from multiples cameras'
    )
    parser.add_argument(
        '--person', '-p', type=int, required=True, help='ID to identity person')
    parser.add_argument(
        '--gesture', '-g', type=int, required=True, help='ID to identity gesture')
    args = parser.parse_args()
    return args.person, args.gesture
gestures = get_gestures()

person_id, gesture_id = get_person_gesture_by_parser()

sequence = 'p{:03d}g{:02d}'.format(person_id, gesture_id)
sequence_folder = os.path.join(options.folder, sequence)

if str(gesture_id) not in gestures:
    log.critical("Invalid GESTURE_ID: {}. \nAvailable gestures: {}",
                 gesture_id, json.dumps(gestures, indent=2))

# Verificando se o id de pessoa informado é válido
if person_id < 1 or person_id > 999:
    log.critical(
        "Invalid PERSON_ID: {}. Must be between 1 and 999.", person_id)

# Exibindo os ids de pessoa e gesto informados
log.info("PERSON_ID: {} GESTURE_ID: {}", person_id, gesture_id)


# Verificando se a pasta para armazenamento das imagens existe e, se não existe, criando-a
if not os.path.exists(options.folder):
    os.makedirs(options.folder)

# Verifica se já existe uma pasta com o mesmo nome da sequência a ser salva, e perguntando ao usuário se deseja
# sobrescrevê-la, caso ela exista
if os.path.exists(sequence_folder):
    log.warn(
        'Path to PERSON_ID={} GESTURE_ID={} already exists.\nWould you like to proceed? All data will be deleted![y/n]',
        person_id, gesture_id)
    answer = input('Insert: ').lower()
    if answer == 'y':
        # Recursively delete a directory tree.
        shutil.rmtree(sequence_folder)

    else:
        sys.exit(0)


# Criando a pasta para armazenamento das imagens da sequência
os.makedirs(sequence_folder)

# cria um objeto do tipo Channel passando o URI do broker como parâmetro
channel = Channel(options.broker_uri)
channels = [Channel(options.broker_uri) for cam in range(len(options.cameras))]
# cria um objeto do tipo Subscription passando o objeto channel como parâmetro
subscription = Subscription(channel)
subscriptions = [Subscription(channels[cam]) for cam in range(len(options.cameras))]
# itera sobre as câmeras presentes nas opções do programa e se inscreve no tópico de cada uma
for camera in options.cameras:
    subscription.subscribe('CameraGateway.{}.Frame'.format(camera.id))

# cria um array de zeros que será utilizado para armazenar a imagem completa
size = (2 * options.cameras[0].config.image.resolution.height,
        2 * options.cameras[0].config.image.resolution.width, 3)
full_image = np.zeros(size, dtype=np.uint8)

# cria um dicionário vazio para armazenar as imagens das câmeras
images_data = {}
# cria um dicionário vazio para armazenar os timestamps de cada imagem
current_timestamps = {}
# cria um dicionário vazio para armazenar as imagens de cada câmera
images = {}

# cria um defaultdict vazio para armazenar os timestamps de cada câmera
timestamps = defaultdict(list)

# inicializa o número de amostras
n_sample = 0

# inicializa a taxa de exibição e a variável de controle para salvar a sequência
display_rate = 2
start_save = False
# inicializa a variável que indica se a sequência foi salva
sequence_saved = False

# inicializa a barra de informações que será exibida na imagem
info_bar_text = "PERSON_ID: {} GESTURE_ID: {} ({})".format(
    person_id, gesture_id, gestures[str(gesture_id)])

def main(topic = 0):
    global start_save,n_sample,sequence_saved,display_rate,info_bar_text
    # loop principal do programa
    while True:
        # consome uma mensagem do canal
        msg = channel.consume()

        # obtém o id da câmera a partir do tópico da mensagem
        camera_id = get_id(msg.topic)
        # verifica se o id da câmera é válido, senão pula para a próxima iteração do loop
        if camera_id is None:
            continue
        #print(camera_id)
        # desempacota a mensagem em um objeto do tipo Image
        pb_image = msg.unpack(Image)
        # verifica se o objeto é válido, senão pula para a próxima iteração do loop
        if pb_image is None:
            continue

        # converte o array de bytes da mensagem em um array numpy
        data = np.fromstring(pb_image.data, dtype=np.uint8)

        # armazena a imagem e o timestamp no dicionário correspondente
        images_data[camera_id] = data
        current_timestamps[camera_id] = dt.utcfromtimestamp(
            msg.created_at).isoformat()

        # verifica se todas as imagens foram recebidas
        if len(images_data) == len(options.cameras):
            # salva as imagens
            if start_save and not sequence_saved:
                for camera in options.cameras:
                    filename = os.path.join(
                        sequence_folder, 'c{:02d}s{:08d}.jpeg'.format(camera.id, n_sample))
                    with open(filename, 'wb') as f:
                        f.write(images_data[camera.id])
                    #timestamps[camera.id].append(current_timestamps[camera.id])
                n_sample += 1
                log.info('Sample {} saved', n_sample)

            # exibe as imagens
            if n_sample % display_rate == 0:
                # decodifica as imagens para o formato BGR
                images = [
                    cv2.imdecode(data, cv2.IMREAD_COLOR)
                    for data in images_data.values()
                ]
                #place_images(full_image, images)
                #display_image = cv2.resize(full_image, (0, 0), fx=0.5, fy=0.5)
                # put recording message
                show_image = images[0]
                draw_info_bar(
                    show_image,
                    info_bar_text,
                    x=50,
                    y=50,
                    draw_circle=start_save and not sequence_saved)

                #if camera_id == 0:
                cv2.imshow('', show_image)
                key = cv2.waitKey(1)
                if key == ord('s'):
                    if not start_save:
                        start_save = True

                    elif not sequence_saved:
                        
                        sequence_saved = True

                if key == ord('p'):
                    start_save = False
                    #timestamps_filename = os.path.join(
                    #        options.folder, '{}_timestamps.json'.format(sequence))
                    #with open(timestamps_filename, 'w') as f:
                    #    json.dump(timestamps, f, indent=2, sort_keys=True)

                if key == ord('q'):
                    break
            # clear dicts
            images_data.clear()
            current_timestamps.clear()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    # Run main with multiprocessing
    processes = []
    with ThreadPoolExecutor(max_workers=2) as executor:#(max_workers=len(options.cameras)) as executor:
        for i in range(1):
            processes.append(executor.submit(main, i))
        for task in as_completed(processes):
            try:
                task.result()
            except Exception as e:
                log.error(e)
    

log.info("Exiting")
