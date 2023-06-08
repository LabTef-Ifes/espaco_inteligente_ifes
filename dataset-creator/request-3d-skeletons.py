import datetime
import json
import os
import re
import socket
import sys
import time
from collections import defaultdict
from enum import Enum
from glob import glob

import numpy as np
from google.protobuf.json_format import MessageToDict
from is_msgs.image_pb2 import ObjectAnnotations
from is_wire.core import Channel, ContentType, Logger, Message, Subscription
from utils import AnnotationsFetcher, load_options

MIN_REQUESTS = 50  # Número mínimo de solicitações
MAX_REQUESTS = 644  # Número máximo de solicitações
DEADLINE_SEC = 5.0  # Prazo limite em segundos
JSON2D = r'p(\d{3})g(\d{2})_c(\d{2})_2d.json'
LOCALIZATION_FILE = 'p{:03d}g{:02d}_3d.json'
log = Logger(name='Request3dSkeletons')
options = load_options(print_options=False)

# Enumeração para representar os diferentes estados do programa
class State(Enum):
    MAKE_REQUESTS = 1
    RECV_REPLIES = 2
    CHECK_END_OF_SEQUENCE_AND_SAVE = 3
    CHECK_FOR_TIMEDOUT_REQUESTS = 4
    EXIT = 5


def get_person_gesture_camera(files):
    # Dicionário de dicionários de listas
    person_gesture_camera_dict = defaultdict(lambda: defaultdict(list))
    # Dicionário de dicionários de dicionários
    quantity_of_annotations = defaultdict(lambda: defaultdict(dict))

    for n, file in enumerate(files):
        # Extrai os IDs de pessoa, gesto e câmera do nome do arquivo de anotação
        matches = re.search(JSON2D,  file)
        if matches is None:
            continue

        person_id = int(matches.group(1))
        gesture_id = int(matches.group(2))
        camera_id = int(matches.group(3))

        # Adiciona as informações de pessoa, gesto e câmera ao dicionário de dicionários de listas
        person_gesture_camera_dict[person_id][gesture_id].append(camera_id)

        # Lê o arquivo de anotação e conta o número de anotações
        annotation_path:str = os.path.join(options.folder,  file)

        with open(annotation_path) as f:
            len_annotations = len(json.load(f)['annotations'])
            quantity_of_annotations[person_id][gesture_id][camera_id] = len_annotations
    return person_gesture_camera_dict, quantity_of_annotations


if not os.path.exists(options.folder):
    log.critical("Folder '{}' doesn't exist", options.folder)

# Obtém a lista de arquivos de anotação na pasta especificada
# Lista de arquivos de anotação 2d
log.debug('Parsing Annotation Files')
# Lista de arquivos de anotação 2d
#annotation_files = list(filter(lambda x: x.endswith('_2d.json'), files))
annotation_files = glob(os.path.join(options.folder, '*_2d.json'))

person_gesture_camera, quantity_of_annotations = get_person_gesture_camera(annotation_files)

cameras_id_list:list = [int(camera_cfg.id) for camera_cfg in options.cameras]
pending_localizations:list = []
num_localizations:dict = defaultdict(dict)

log.debug('Checking if detections files already exist')
#???
for person_id, gestures in person_gesture_camera.items():
    for gesture_id, camera_ids in gestures.items():
        # Obtém o número de anotações para a combinação de pessoa, gesto e câmera atual

        # Verifica se já existe um arquivo de localização para a combinação de pessoa e gesto atual
        file = os.path.join(options.folder, LOCALIZATION_FILE.format(person_id, gesture_id))
        if os.path.exists(file):
            with open(file) as f:
                n_loc = len(json.load(f)['localizations'])
            if n_loc == n_an[0]:
                log.info('PERSON_ID: {:03d} GESTURE_ID: {:02d} | Already have localization file.', person_id, gesture_id)
                continue

        n_an:list = list(quantity_of_annotations[person_id][gesture_id].values())
        print('n_an=', n_an) # teste visual

        # Verifica se todos os valores de anotações são iguais ao primeiro valor (anotações inconsistentes)
        # Deveria tirar o not?
        #if not all(map(lambda x: x == n_an[0], n_an)):
        if all(map(lambda x: x == n_an[0], n_an)):
            log.warn("PERSON_ID: {:03d} GESTURE_ID: {:02d} | Annotations size inconsistent.", person_id, gesture_id)
            continue

        # Verifica se os IDs das câmeras no arquivo correspondem aos IDs das câmeras especificadas nas opções
        if set(camera_ids) != set(cameras_id_list):
            log.warn("PERSON_ID: {:03d} GESTURE_ID: {:02d} | Can't find all detections file.", person_id, gesture_id)
            continue

        # Registra o número de localizações esperadas para a combinação de pessoa e gesto atual
        num_localizations[person_id][gesture_id] = n_an[0] # Por que o primeiro?

        # Adiciona as informações da localização pendente à lista de localizações pendentes
        pending_localizations.append({
            'person_id': person_id,
            'gesture_id': gesture_id,
            'num_localizations': n_an[0]
        })

if not pending_localizations:
    log.info("Exiting...")
    sys.exit(0)

# Comunicação
channel = Channel(options.broker_uri)
subscription = Subscription(channel)

requests:dict = {}

localizations_received:dict = defaultdict(lambda: defaultdict(dict))

annotations_fetcher:AnnotationsFetcher = AnnotationsFetcher(pending_localizations=pending_localizations, cameras=cameras_id_list, base_folder=options.folder)

state = State.MAKE_REQUESTS
while True:
    if state == State.MAKE_REQUESTS:
        state = State.RECV_REPLIES
        
        if len(requests) >= MIN_REQUESTS:
            while len(requests) <= MAX_REQUESTS:
                person_id, gesture_id, pos, annotations = annotations_fetcher.next()
                if pos is None:
                    if len(requests) == 0:
                        state = State.EXIT
                    break

                msg = Message(reply_to=subscription, content_type=ContentType.JSON)
                body = json.dumps({'list': annotations}).encode('utf-8')
                msg.body = body
                msg.timeout = DEADLINE_SEC
                channel.publish(msg, topic='SkeletonsGrouper.Localize')
                requests[msg.correlation_id] = {
                    'body': body,
                    'person_id': person_id,
                    'gesture_id': gesture_id,
                    'pos': pos,
                    'requested_at': time.time()
                }

    elif state == State.RECV_REPLIES:
        try:
            msg = channel.consume(timeout=DEADLINE_SEC)
            if msg.status.ok():
                localizations = msg.unpack(ObjectAnnotations)
                correlation_id = msg.correlation_id
                if correlation_id in requests:
                    person_id = requests[correlation_id]['person_id']
                    gesture_id = requests[correlation_id]['gesture_id']
                    pos = requests[correlation_id]['pos']
                    localizations_received[person_id][gesture_id][pos] = MessageToDict(
                        localizations,
                        preserving_proto_field_name=True,
                        including_default_value_fields=True)
                    requests.pop(correlation_id)

            state = State.CHECK_END_OF_SEQUENCE_AND_SAVE
        except socket.timeout:
            state = State.CHECK_FOR_TIMEDOUT_REQUESTS

    elif state == State.CHECK_END_OF_SEQUENCE_AND_SAVE:
        done_sequences:list[tuple] = []
        # Error para p001g03???
        for person_id, gestures in localizations_received.items():
            for gesture_id, localizations_dict in gestures.items():

                if len(localizations_dict) < num_localizations[person_id][gesture_id]:
                    continue
                
                output_localizations = {
                    'localizations': [x[1] for x in sorted(localizations_dict.items())],
                    'created_at': datetime.datetime.now().isoformat()
                }
                filename = LOCALIZATION_FILE.format(person_id, gesture_id)
                filepath = os.path.join(options.folder, filename)
                with open(filepath, 'w') as f:
                    json.dump(output_localizations, f, indent=2)

                done_sequences.append((person_id, gesture_id))

                localizations_count = [len(localization['objects']) for localization in output_localizations['localizations']]

                unique_counts, count_occurrences = np.unique(localizations_count, return_counts=True)
                count_dict = dict(zip(unique_counts, count_occurrences))
                count_dict_str = ", ".join(["{}: {}".format(k, v) for k, v in count_dict.items()])

                log.info('Saved: PERSON_ID: {:03d} GESTURE_ID: {:02d} | Count: {}',
                         person_id, gesture_id, count_dict_str)

        for person_id, gesture_id in done_sequences:
            localizations_received[person_id].pop(gesture_id)

        state = State.MAKE_REQUESTS

    elif state == State.CHECK_FOR_TIMEDOUT_REQUESTS:
        current_time = time.time()
        timedout_requests = [
            correlation_id for correlation_id, request in requests.items() if current_time - request['requested_at'] >= DEADLINE_SEC
        ]
        for correlation_id in timedout_requests:
            person_id = requests[correlation_id]['person_id']
            gesture_id = requests[correlation_id]['gesture_id']
            pos = requests[correlation_id]['pos']
            requests.pop(correlation_id)

            log.warn('Timed out: PERSON_ID: {:03d} GESTURE_ID: {:02d} | Position: {}',
                     person_id, gesture_id, pos)

        state = State.MAKE_REQUESTS

    elif state == State.EXIT:
        break

log.info("Exiting...")
sys.exit(0)
