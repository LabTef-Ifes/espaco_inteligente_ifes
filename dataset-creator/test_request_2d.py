# -*- coding: utf-8 -*-
import re
import datetime
import json
import os
import socket
import sys
import time
from collections import defaultdict
from enum import Enum,auto
from glob import glob

import cv2
from is_wire.core import Channel, Logger, Message, Subscription
from utils import FrameVideoFetcher, load_options, make_pb_image
import numpy as np
import numpy.typing as npt

from google.protobuf.json_format import MessageToJson,MessageToDict
from is_msgs.image_pb2 import Image, ObjectAnnotations
from is_wire.core import Channel, Message, Subscription
# Comentários explicativos gerados pelo chatGPT 29/04/2023. Não havia qualquer comentário no código original.

class Skeleton2D:
# Definição de constantes
    MIN_REQUESTS = 5
    MAX_REQUESTS = 15
    DEADLINE_SEC = 5.0
    JSON2D_FORMAT = '{}_2d.json'

    def __init__(self):
        """Inicializa o objeto de rastreamento de esqueletos 2D.
        """        
        self.options = load_options(print_options=False)
        self.check_path()

        self.log = Logger(name='Request2dSkeletons')
        self.video_files:list = glob(os.path.join(self.options.folder, '*.mp4'))

        self.requests:dict = {}
        self.annotations_received:defaultdict = defaultdict(dict)
        
        self.state = None # Estado atual do loop em self.run()

        #self.pending_videos,self.n_annotations = self.get_pending_videos()

        #self.channel,self.subscription = self.start_communication()
        

        #self.frame_fetcher:FrameVideoFetcher = FrameVideoFetcher(
        #            video_files=self.pending_videos, base_folder=self.options.folder)

    def array2image(
    image: npt.NDArray[np.uint8],
    encode_format: str = ".jpeg",
    compression_level: float = 0.8,
    ) -> Image:
        if encode_format == ".jpeg":
            params = [cv2.IMWRITE_JPEG_QUALITY, int(compression_level * (100 - 0) + 0)]
        elif encode_format == ".png":
            params = [cv2.IMWRITE_PNG_COMPRESSION, int(compression_level * (9 - 0) + 0)]
        else:
            return Image()
        cimage = cv2.imencode(ext=encode_format, img=image, params=params)
        return Image(data=cimage[1].tobytes())

    def get_images_list(self):
        pattern = re.compile(r'^p\d{3}g\d{2}$')
        folders = [f.path for f in os.scandir('videos') if re.match(pattern,f.name)]
        
        for pg in folders:
            for cam in range(0,4):
                yield ([x.path for x in os.scandir(pg) if x.name.startswith(f'c{cam:02d}')])
        

    def main(self) -> None:
        """
        Main method for processing images and making requests.

        This method prepares a request, processes images, and makes a request to a specific topic.
        It waits for a reply with a timeout of 1.0 seconds and saves the received annotations to a JSON file.

        Raises:
            NameError: If the directory name is not found in the image path.

        Returns:
            None
        """
        # Prepare request
        for img_list in self.get_images_list():
            regex_pattern = re.compile(r'[^/]+/([^/]+)/')

            # Use the regex pattern to find the second directory name
            match = regex_pattern.search(img_list[0])
            if match:
                dir_name = match.group(1)
            else:
                raise NameError('Directory name not found. Searching for pXXXgXX')

            for img in img_list:

                array = cv2.imread(img)
                image = array2image(image=array)
                request = Message(content=image, reply_to=self.subscription)
                # Make request
                ti = time.time()
                self.channel.publish(request, topic="SkeletonsDetector.Detect")

                # Wait for reply with 1.0 seconds timeout
                try:
                    camera_code = re.compile(r'/([^/]+)/c\d+s\d+\.jpeg$') #c00
                    # Use the regex pattern to find the camera name
                    match = camera_code.search(img)
                    if match:
                        camera_name = match.group(1)
                    reply = self.channel.consume(timeout=1.0)
                    tf = time.time()
                    print((tf - ti)*1000)
                    annotations = reply.unpack(ObjectAnnotations)
                    print('RPC Status:', reply.status, '\nReply:', annotations)
                    with open(
                        file=f"{dir_name+camera_name}_2d.json",
                        mode="a",
                        encoding="utf-8",
                    ) as file:
                        content = MessageToJson(annotations, indent=2)
                        file.write(content)
                except socket.timeout:
                    print('No reply :(')

    def _make_request(self):
        self.state = State.RECV_REPLIES  # muda o estado para receber respostas
        if len(self.requests) < self.MIN_REQUESTS:  # se a quantidade de pedidos for menor que o minimo exigido
            # enquanto a quantidade de pedidos for menor ou igual ao máximo permitido
            while len(self.requests) <= self.MAX_REQUESTS:
                # obtém informações do próximo frame do vídeo
                base_name, frame_id, frame = self.frame_fetcher.next()
                if frame is None:  # se o frame não for encontrado
                    if not self.requests:  # se não houver pedidos
                        self.state = State.EXIT  # muda o estado para sair
                    break
                # converte o frame em um objeto de imagem protobuf
                pb_image = make_pb_image(frame)
                # cria uma mensagem com a imagem e uma assinatura
                msg = Message(content=pb_image, reply_to=self.subscription)
                msg.timeout = self.DEADLINE_SEC  # define um tempo limite para receber uma resposta
                
                # publica a mensagem no canal
                self.channel.publish(msg, topic='SkeletonsDetector.Detect')

                self.requests[msg.correlation_id] = {  # armazena o pedido para rastreamento
                    'content': pb_image,
                    'base_name': base_name,
                    'frame_id': frame_id,
                    'requested_at': time.time()
                }
    def _recv_replies(self):
        
        try:
            # obtém uma mensagem do canal com um tempo limite
            msg = self.channel.consume(timeout=3.0)
            if msg.status.ok():  # se a mensagem estiver ok
                # desempacota as anotações de objetos
                annotations = msg.unpack(ObjectAnnotations)
                correlation_id = msg.correlation_id  # obtém a assinatura da mensagem
                if correlation_id in self.requests:  # se a assinatura estiver nos pedidos
                    # obtém o nome base do arquivo
                    base_name = self.requests[correlation_id]['base_name']
                    frame_id = self.requests[correlation_id]['frame_id']  # obtém o ID do frame
                    self.annotations_received[base_name][frame_id] = MessageToDict(  # armazena as anotações recebidas
                        annotations,
                        preserving_proto_field_name=True,
                        including_default_value_fields=True)
                    # remove o pedido da lista de pedidos ativos
                    self.requests.pop(correlation_id)

        except socket.timeout:  # se houver uma exceção de tempo limite de soquete
            # muda o estado para verificar pedidos com tempo limite excedido
            self.state = State.CHECK_FOR_TIMEOUTED_REQUESTS
        else:
            # muda o estado para verificar o fim do vídeo e salvar
            self.state = State.CHECK_END_OF_VIDEO_AND_SAVE

    def _check_end_of_video_and_save(self):
        # para cada nome base de arquivo nas anotações recebidas
        for base_name in list(self.annotations_received.keys()):

            filename = os.path.join(self.options.folder,
                                        self.JSON2D_FORMAT.format(base_name))

            # obtém o dicionário de anotações
            annotations_dict:dict = self.annotations_received[base_name]

            # se todas as anotações estiverem presentes
            if len(annotations_dict) == self.n_annotations[base_name]:
                output_annotations = {  # cria um objeto de saída de anotações
                    'annotations': [x[1] for x in sorted(annotations_dict.items())],
                    'created_at': datetime.datetime.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(output_annotations, f, indent=2)

                self.annotations_received.pop(base_name)

                self.log.info('{} has been saved.', filename)

        self.state = State.CHECK_FOR_TIMEOUTED_REQUESTS

    def _check_for_timeouted_requests(self):
        def publish_message(message,topic:str='SkeletonsDetector.Detect'):
            self.channel.publish(message, topic=topic)

        # cria um novo dicionário vazio para as novas requisições
        new_requests:dict = {}

        # percorre todas as chaves do dicionário requests
        for correlation_id in list(self.requests.keys()):
            # recupera a requisição com a chave correlation_id
            single_request = self.requests[correlation_id]

            # verifica se a requisição ainda não passou do DEADLINE_SEC
            if (single_request['requested_at'] + self.DEADLINE_SEC) > time.time():
                continue

            # se passou do prazo, cria uma nova mensagem com a requisição e publica no tópico 'SkeletonsDetector.Detect'
            msg = Message(content=single_request['content'], reply_to=self.subscription)
            msg.timeout = self.DEADLINE_SEC

            publish_message(msg,topic='SkeletonsDetector.Detect')

            # adiciona uma nova entrada ao dicionário new_requests com o correlation_id como chave
            new_requests[msg.correlation_id] = {
                'content': single_request['content'],
                'base_name': single_request['base_name'],
                'frame_id': single_request['frame_id'],
                'requested_at': time.time()
            }

            # remove a requisição do dicionário requests
            self.requests.pop(correlation_id)

            # exibe uma mensagem de log informando que a mensagem expirou
            self.log.warn("Message '{}' timeouted. Sending another request.", correlation_id)

        # atualiza o dicionário requests com as novas requisições
        self.requests.update(new_requests)

        # muda o estado para State.MAKE_REQUESTS
        self.state = State.MAKE_REQUESTS
    def run(self):
        if self.pending_videos:
                
            self.state = State.MAKE_REQUESTS
            while True:
                if self.state is State.MAKE_REQUESTS: # se o estado atual é fazer pedidos
                    self._make_request()
                
                elif self.state is State.RECV_REPLIES: # se o estado atual é receber respostas
                    self._recv_replies()
                
                elif self.state is State.CHECK_END_OF_VIDEO_AND_SAVE: # se o estado atual é verificar o fim do vídeo e salvar
                    self._check_end_of_video_and_save()
                
                elif self.state is State.CHECK_FOR_TIMEOUTED_REQUESTS: # se o estado atual é verificar pedidos com tempo limite excedido
                    self._check_for_timeouted_requests()
                
                elif self.state is State.EXIT: # se o estado atual é sair
                    break
            self.log.info("Completed!")
        else:
            self.log.info("No videos to process!")
    def check_path(self):
        # Verificação da existência da pasta especificada nas opções
        if not os.path.exists(self.options.folder):
            self.log.critical("Folder '{}' doesn't exist", self.options.folder)
            sys.exit(-1)

    def start_communication(self):
        # Comunicação
        channel = Channel(self.options.broker_uri)
        subscription = Subscription(channel)
        return channel, subscription

    def get_pending_videos(self):
        # Criação de lista de vídeos a serem processados e do número de frames em cada um
        pending_videos = []
        n_annotations = {}
        for video_file in self.video_files:
            video_file = video_file.split('/')[-1] #raw filename
            base_name = video_file.split('.')[0] #pNNNgNN
            annotation_file = self.JSON2D_FORMAT.format(base_name) #p001g01c00_2d.json
            
            annotation_path = os.path.join(self.options.folder, annotation_file) #videos/p001g01c00_2d.json
            video_path = os.path.join(self.options.folder, video_file) #videos/p001g01c00.mp4

            cap = cv2.VideoCapture(video_path)
            n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if os.path.exists(annotation_path):
                with open(annotation_path, 'r') as f:
                    annotations_data = json.load(f)

                num_annotations_on_file = len(annotations_data['annotations'])

                if num_annotations_on_file == n_frames:
                    self.log.info(
                        "Video '{}' already annotated at '{}' with {} annotations",
                        video_file, annotations_data['created_at'],
                        num_annotations_on_file)
                    continue

            pending_videos.append(video_file)
            n_annotations[base_name] = n_frames

        if pending_videos:
            self.log.info('{}',pending_videos)
        else:            
            self.log.info("Exiting...")
        return pending_videos,n_annotations
        

# Definição de estados para a máquina de estados
class State(Enum):
    MAKE_REQUESTS = auto()
    RECV_REPLIES = auto()
    CHECK_END_OF_VIDEO_AND_SAVE = auto()
    CHECK_FOR_TIMEOUTED_REQUESTS = auto()
    EXIT = auto()

if __name__ == '__main__':
    request_skeleton = Skeleton2D()
    #request_skeleton.run()
    print(request_skeleton.get_images_list())
    