# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import shutil
import argparse
from datetime import datetime as dt
from collections import defaultdict, OrderedDict
from subprocess import PIPE, STDOUT
import threading
import cv2
import numpy as np
from utils import load_options
from is_msgs.image_pb2 import Image
from is_wire.core import Channel, Subscription, Message, Logger

# Conferir se é melhor fazer o imwrite direto ou salvar tudo e fazer depois
# Estou fazendo multithreading, que compartilha recursos entre as threads. Para isolar os recursos, usar multiprocessing
"""_summary_
"""
NUMBER_OF_THREADS = 4

def get_id(topic):
    """A partir do nome do tópico 'CameraGateway.(\d+).Frame' retorna o id da câmera

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
    """Enquadra 4 imagens em uma única imagem

    Args:
        output_image_ (_type_): _description_
        images_ (_type_): _description_
    """
    h, w = images_[0].shape[0:2]
    output_image_ = output_image.copy()

    output_image_[0:h, 0:w, :] = images_[0]
    output_image_[0:h, w:2 * w, :] = images_[1]
    output_image_[h:2 * h, 0:w, :] = images_[2]
    output_image_[h:2 * h, w:2 * w, :] = images_[3]

    return output_image_

def draw_info_bar(image, text, x, y,
                  background_color=(0, 0, 0),
                  text_color=(255, 255, 255),
                  draw_circle=False):
    """Draw a bar on top of the image

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

    # Verificando se o id de pessoa informado é válido
    if args.person < 1 or args.person > 999:
        log.critical(
            "Invalid PERSON_ID: {}. Must be between 1 and 999.", args.person)

    return args.person, args.gesture


# Carregando as opções de configuração
options = load_options(print_options=False)
# Iniciando o logger
log = Logger(name='capture-images')
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

gestures = get_gestures()

person_id, gesture_id = get_person_gesture_by_parser()

sequence = 'p{:03d}g{:02d}'.format(person_id, gesture_id)
sequence_folder = os.path.join(options.folder, sequence)

# Exibindo os ids de pessoa e gesto informados
log.info("PERSON_ID: {} GESTURE_ID: {}", person_id, gesture_id)

# Verificando se a pasta para armazenamento das imagens existe e, se não existe, criando-a
if not os.path.exists(options.folder):
    os.makedirs(options.folder)

# Verificando se já existe uma pasta com o mesmo nome da sequência a ser salva, e perguntando ao usuário se deseja
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

#subscription_list = [Subscription(channel) for _ in range(len(options.cameras))]
subscription=Subscription(channel)

for i in range(len(options.cameras)):
    subscription.subscribe(f'CameraGateway.{i}.Frame')

# cria um array de zeros que será utilizado para armazenar a imagem completa
size = (2 * options.cameras[0].config.image.resolution.height,
        2 * options.cameras[0].config.image.resolution.width, 
        3)
full_image = np.zeros(size, dtype=np.uint8)

start_save = False
def consume_images(lock:threading.Lock,topic:int = 0):
    global start_save

    #images_dict = defaultdict(list)
    # loop principal do programa
    while True:
        # consome uma mensagem do canal
        lock.acquire()
        msg = channel.consume()
        lock.release()
        # obtém o id da câmera a partir do tópico da mensagem
        camera_id = get_id(msg.topic)
        # verifica se o id da câmera é válido, senão pula para a próxima iteração do loop
        if camera_id is None:
            continue
        # desempacota a mensagem em um objeto do tipo Image
        pb_image = msg.unpack(Image)
        # verifica se o objeto é válido, se não, pula para a próxima iteração do loop
        if pb_image is None:
            continue

        # converte o array de bytes da mensagem em um array numpy
        data = np.fromstring(pb_image.data, dtype=np.uint8)
        cv2.imshow('Camera {}'.format(camera_id), data)
        # salva as imagens
        if start_save:
            filename = os.path.join(
                sequence_folder, 'c{:02d}s{:08d}.jpeg'.format(camera_id, n_sample))
            lock.acquire()
            cv2.imwrite(filename, data)
            lock.release()

            n_sample += 1
            log.info('Sample {} saved', n_sample) #Pode dar erro durante o paralelismo

        if cv2.waitKey(1) & 0xFF == ord('s'):
            start_save = True
            log.info('Start saving samples')
        
        if cv2.waitKey(1) & 0xFF == ord('p'):
            start_save = False
            log.info('Stop saving samples')
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
if __name__ == '__main__':
    lock = threading.Lock()
    threads = []
    for i in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=consume_images, args=(lock,))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
