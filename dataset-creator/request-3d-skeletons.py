import datetime
import json
import os
import re
import socket
import sys
import time
from collections import defaultdict
from enum import Enum

import numpy as np
from google.protobuf.json_format import MessageToDict
from is_msgs.image_pb2 import ObjectAnnotations
from is_wire.core import Channel, ContentType, Logger, Message, Subscription
from utils import AnnotationsFetcher, load_options

MIN_REQUESTS = 50  # Número mínimo de solicitações
MAX_REQUESTS = 644  # Número máximo de solicitações
DEADLINE_SEC = 5.0  # Prazo limite em segundos

# Enumeração para representar os diferentes estados do programa
class State(Enum):
    MAKE_REQUESTS = 1
    RECV_REPLIES = 2
    CHECK_END_OF_SEQUENCE_AND_SAVE = 3
    CHECK_FOR_TIMEDOUT_REQUESTS = 4
    EXIT = 5

LOCALIZATION_FILE = 'p{:03d}g{:02d}_3d.json'

log = Logger(name='Request3dSkeletons')
options = load_options(print_options=False)

if not os.path.exists(options.folder):
    log.critical("Folder '{}' doesn't exist", options.folder)

# Obtém a lista de arquivos de anotação na pasta especificada
files = next(os.walk(options.folder))[2]  # Apenas arquivos do primeiro nível da pasta

# Lista de arquivos de anotação 2d
annotation_files = list(filter(lambda x: x.endswith('_2d.json'), files))

log.debug('Parsing Annotation Files')
entries = defaultdict(lambda: defaultdict(list))
n_annotations = defaultdict(lambda: defaultdict(dict))

for annotation_file, n in zip(annotation_files, range(len(annotation_files))):
    # Extrai os IDs de pessoa, gesto e câmera do nome do arquivo de anotação
    matches = re.search("p([0-9]{3})g([0-9]{2})c([0-9]{2})_2d.json", annotation_file)
    if matches is None:
        continue
    person_id = int(matches.group(1))
    gesture_id = int(matches.group(2))
    camera_id = int(matches.group(3))
    entries[person_id][gesture_id].append(camera_id)

    # Lê o arquivo de anotação e conta o número de anotações
    annotation_path = os.path.join(options.folder, annotation_file)
    with open(annotation_path, 'r') as f:
        n = len(json.load(f)['annotations'])
        n_annotations[person_id][gesture_id][camera_id] = n

log.debug('Checking if detections files already exist')
cameras = [int(camera_cfg.id) for camera_cfg in options.cameras]
pending_localizations = []
n_localizations = defaultdict(dict)
for person_id, gestures in entries.items():
    for gesture_id, camera_ids in gestures.items():
        # Verifica se os IDs das câmeras no arquivo correspondem aos IDs das câmeras especificadas nas opções
        if set(camera_ids) != set(cameras):
            log.warn("PERSON_ID: {:03d} GESTURE_ID: {:02d} | Can't find all detections file.", person_id, gesture_id)
            continue

        # Obtém o número de anotações para a combinação de pessoa, gesto e câmera atual
        n_an = list(n_annotations[person_id][gesture_id].values())

        # Verifica se todos os valores de anotações são iguais ao primeiro valor (anotações inconsistentes)
        if not all(map(lambda x: x == n_an[0], n_an)):
            log.warn("PERSON_ID: {:03d} GESTURE_ID: {:02d} | Annotations size inconsistent.", person_id, gesture_id)
            continue

        # Verifica se já existe um arquivo de localização para a combinação de pessoa e gesto atual
        file = os.path.join(options.folder, LOCALIZATION_FILE.format(person_id, gesture_id))
        if os.path.exists(file):
            with open(file, 'r') as f:
                n_loc = len(json.load(f)['localizations'])
            if n_loc == n_an[0]:
                log.info('PERSON_ID: {:03d} GESTURE_ID: {:02d} | Already have localization file.', person_id, gesture_id)
                continue

        # Registra o número de localizações esperadas para a combinação de pessoa e gesto atual
        n_localizations[person_id][gesture_id] = n_an[0]

        # Adiciona as informações da localização pendente à lista de localizações pendentes
        pending_localizations.append({
            'person_id': person_id,
            'gesture_id': gesture_id,
            'n_localizations': n_an[0]
        })

if not pending_localizations:
    log.info("Exiting...")
    sys.exit(0)

# Comunicação
channel = Channel(options.broker_uri)
subscription = Subscription(channel)

requests = {}
localizations_received = defaultdict(lambda: defaultdict(dict))
state = State.MAKE_REQUESTS
annotations_fetcher = AnnotationsFetcher(pending_localizations=pending_localizations, cameras=cameras, base_folder=options.folder)

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
                cid = msg.correlation_id
                if cid in requests:
                    person_id = requests[cid]['person_id']
                    gesture_id = requests[cid]['gesture_id']
                    pos = requests[cid]['pos']
                    localizations_received[person_id][gesture_id][pos] = MessageToDict(
                        localizations,
                        preserving_proto_field_name=True,
                        including_default_value_fields=True)
                    del requests[cid]

            state = State.CHECK_END_OF_SEQUENCE_AND_SAVE
        except socket.timeout:
            state = State.CHECK_FOR_TIMEDOUT_REQUESTS

    elif state == State.CHECK_END_OF_SEQUENCE_AND_SAVE:
        done_sequences = []
        for person_id, gestures in localizations_received.items():
            for gesture_id, localizations_dict in gestures.items():

                if len(localizations_dict) < n_localizations[person_id][gesture_id]:
                    continue

                output_localizations = {
                    'localizations': [x[1] for x in sorted(localizations_dict.items())],
                    'created_at': datetime.datetime.now().isoformat()
                }
                filename = 'p{:03d}g{:02d}_3d.json'.format(person_id, gesture_id)
                filepath = os.path.join(options.folder, filename)
                with open(filepath, 'w') as f:
                    json.dump(output_localizations, f, indent=2)

                done_sequences.append((person_id, gesture_id))

                localizations_count = [
                    len(l['objects']) for l in output_localizations['localizations']
                ]
                count_dict = map(lambda x: list(map(str, x)),
                                 np.unique(localizations_count, return_counts=True))
                count_dict_str = ", ".join(["{}: {}".format(k, v) for k, v in count_dict])

                log.info('Saved: PERSON_ID: {:03d} GESTURE_ID: {:02d} | Count: {}',
                         person_id, gesture_id, count_dict_str)

        for person_id, gesture_id in done_sequences:
            localizations_received[person_id].pop(gesture_id)

        state = State.MAKE_REQUESTS

    elif state == State.CHECK_FOR_TIMEDOUT_REQUESTS:
        current_time = time.time()
        timedout_requests = [
            cid for cid, request in requests.items() if current_time - request['requested_at'] >= DEADLINE_SEC
        ]
        for cid in timedout_requests:
            person_id = requests[cid]['person_id']
            gesture_id = requests[cid]['gesture_id']
            pos = requests[cid]['pos']
            log.warn('Timed out: PERSON_ID: {:03d} GESTURE_ID: {:02d} | Position: {}',
                     person_id, gesture_id, pos)
            del requests[cid]

        state = State.MAKE_REQUESTS

    elif state == State.EXIT:
        break

log.info("Exiting...")
sys.exit(0)
