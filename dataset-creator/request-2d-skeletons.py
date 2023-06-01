# -*- coding: utf-8 -*-
import os
import cv2
import json
import time
import socket
import datetime
from collections import defaultdict
from enum import Enum
from google.protobuf.json_format import MessageToDict
import sys
from is_wire.core import Channel, Subscription, Message, Logger
from is_msgs.image_pb2 import ObjectAnnotations
from utils import load_options, make_pb_image, FrameVideoFetcher

# Comentários explicativos gerados pelo chatGPT 29/04/2023. Não havia qualquer comentário no código original.

# Definição de constantes
MIN_REQUESTS = 5
MAX_REQUESTS = 10
DEADLINE_SEC = 15.0


# Definição de estados para a máquina de estados
class State(Enum):
    MAKE_REQUESTS = 1
    RECV_REPLIES = 2
    CHECK_END_OF_VIDEO_AND_SAVE = 3
    CHECK_FOR_TIMEOUTED_REQUESTS = 4
    EXIT = 5


# Configuração de logging e carregamento de opções
log = Logger(name='Request2dSkeletons')
options = load_options(print_options=False)

# Verificação da existência da pasta especificada nas opções
if not os.path.exists(options.folder):
    log.critical("Folder '{}' doesn't exist", options.folder)
    sys.exit(-1)

# Carregamento da lista de arquivos de vídeo na pasta
# Por que [2]???
files = next(os.walk(options.folder))[2]  # only files from first folder level
video_files = list(filter(lambda x: x.endswith('.mp4'), files))

# Criação de lista de vídeos a serem processados e do número de frames em cada um
pending_videos = []
n_annotations = {}
for video_file in video_files:
    base_name = video_file.split('.')[0]
    annotation_file = '{}_2d.json'.format(base_name)
    annotation_path = os.path.join(options.folder, annotation_file)
    video_path = os.path.join(options.folder, video_file)
    cap = cv2.VideoCapture(video_path)
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if os.path.exists(annotation_path):
        with open(annotation_path, 'r') as f:
            annotations_data = json.load(f)

        n_annotations_on_file = len(annotations_data['annotations'])

        if n_annotations_on_file == n_frames:
            log.info(
                "Video '{}' already annotated at '{}' with {} annotations",
                video_file, annotations_data['created_at'],
                n_annotations_on_file)
            continue

    pending_videos.append(video_file)
    n_annotations[base_name] = n_frames

if not pending_videos:
    log.info("Exiting...")
    sys.exit(-1)

# Inicialização de variáveis e objetos
channel = Channel(options.broker_uri)
subscription = Subscription(channel)
requests = {}
annotations_received = defaultdict(dict)
state = State.MAKE_REQUESTS
frame_fetcher = FrameVideoFetcher(
    video_files=pending_videos, base_folder=options.folder)

while True:

    if state == State.MAKE_REQUESTS:  # se o estado atual é fazer pedidos
        if len(requests) < MIN_REQUESTS:  # se a quantidade de pedidos for menor que o minimo exigido
            # enquanto a quantidade de pedidos for menor ou igual ao máximo permitido
            while len(requests) <= MAX_REQUESTS:
                # obtém informações do próximo frame do vídeo
                base_name, frame_id, frame = frame_fetcher.next()
                if frame is None:  # se o frame não for encontrado
                    if not requests:  # se não houver pedidos
                        state = State.EXIT  # muda o estado para sair
                    break
                # converte o frame em um objeto de imagem protobuf
                pb_image = make_pb_image(frame)
                # cria uma mensagem com a imagem e uma assinatura
                msg = Message(content=pb_image, reply_to=subscription)
                msg.timeout = DEADLINE_SEC  # define um tempo limite para receber uma resposta
                # publica a mensagem no canal
                channel.publish(msg, topic='SkeletonsDetector.Detect')
                requests[msg.correlation_id] = {  # armazena o pedido para rastreamento
                    'content': pb_image,
                    'base_name': base_name,
                    'frame_id': frame_id,
                    'requested_at': time.time()
                }
        state = State.RECV_REPLIES  # muda o estado para receber respostas

    elif state == State.RECV_REPLIES:  # se o estado atual é receber respostas
        try:
            # obtém uma mensagem do canal com um tempo limite de 1 segundo
            msg = channel.consume(timeout=1.0)
            if msg.status.ok():  # se a mensagem estiver ok
                # desempacota as anotações de objetos
                annotations = msg.unpack(ObjectAnnotations)
                cid = msg.correlation_id  # obtém a assinatura da mensagem
                if cid in requests:  # se a assinatura estiver nos pedidos
                    # obtém o nome base do arquivo
                    base_name = requests[cid]['base_name']
                    frame_id = requests[cid]['frame_id']  # obtém o ID do frame
                    annotations_received[base_name][frame_id] = MessageToDict(  # armazena as anotações recebidas
                        annotations,
                        preserving_proto_field_name=True,
                        including_default_value_fields=True)
                    # remove o pedido da lista de pedidos ativos
                    del requests[cid]

            # muda o estado para verificar o fim do vídeo e salvar
            state = State.CHECK_END_OF_VIDEO_AND_SAVE

        except socket.timeout:  # se houver uma exceção de tempo limite de soquete
            # muda o estado para verificar pedidos com tempo limite excedido
            state = State.CHECK_FOR_TIMEOUTED_REQUESTS

    elif state == State.CHECK_END_OF_VIDEO_AND_SAVE:  # se o estado atual é verificar o fim do vídeo e salvar
        # para cada nome base de arquivo nas anotações recebidas
        for base_name in list(annotations_received.keys()):
            # obtém o dicionário de anotações
            annotations_dict = annotations_received[base_name]
            # se todas as anotações estiverem presentes
            if len(annotations_dict) == n_annotations[base_name]:
                output_annotations = {  # cria um objeto de saída de anotações
                    'annotations': [x[1] for x in sorted(annotations_dict.items())],
                    'created_at': datetime.datetime.now().isoformat()
                }
                filename = os.path.join(options.folder,
                                        '{}_2d.json'.format(base_name))
                with open(filename, 'w') as f:
                    json.dump(output_annotations, f, indent=2)
                del annotations_received[base_name]
                log.info('{} has been saved.', filename)

        state = State.CHECK_FOR_TIMEOUTED_REQUESTS

    # Caso o estado seja State.CHECK_FOR_TIMEOUTED_REQUESTS:
    elif state == State.CHECK_FOR_TIMEOUTED_REQUESTS:
        # cria um novo dicionário vazio para as novas requisições
        new_requests = {}

        # percorre todas as chaves do dicionário requests
        for cid in list(requests.keys()):
            # recupera a requisição com a chave cid
            request = requests[cid]

            # verifica se a requisição ainda não passou do DEADLINE_SEC
            if (request['requested_at'] + DEADLINE_SEC) > time.time():
                continue

            # se passou do prazo, cria uma nova mensagem com a requisição e publica no tópico 'SkeletonsDetector.Detect'
            msg = Message(content=request['content'], reply_to=subscription)
            msg.timeout = DEADLINE_SEC
            channel.publish(msg, topic='SkeletonsDetector.Detect')

            # adiciona uma nova entrada ao dicionário new_requests com o correlation_id como chave
            new_requests[msg.correlation_id] = {
                'content': request['content'],
                'base_name': request['base_name'],
                'frame_id': request['frame_id'],
                'requested_at': time.time()
            }

            # remove a requisição do dicionário requests
            requests.pop(cid)

            # exibe uma mensagem de log informando que a mensagem expirou
            log.warn("Message '{}' timeouted. Sending another request.", cid)

        # atualiza o dicionário requests com as novas requisições
        requests.update(new_requests)

        # muda o estado para State.MAKE_REQUESTS
        state = State.MAKE_REQUESTS

    elif state == State.EXIT:
        log.info("Exiting...")
        break

    else:
        state = State.MAKE_REQUESTS
