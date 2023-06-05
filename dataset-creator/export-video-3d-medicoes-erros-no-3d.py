# -*- coding: utf-8 -*-
import argparse
import csv
import json
import math
import os
import statistics
import time
from collections import OrderedDict
from itertools import permutations
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pika
from analysis import SkeletonsCoord
from google.protobuf.json_format import ParseDict
from is_msgs.image_pb2 import HumanKeypoints as HKP,ObjectAnnotations
from is_wire.core import Logger
from mpl_toolkits.mplot3d import Axes3D
from Parameters import Parameter
import Plota_graficos
from utils import load_options
from video_loader import MultipleVideoLoader

# RGB fixado???
CAPTURA = 'RGB'
log = Logger(name='Export-Video')

colors = list(permutations([0, 255, 85, 170], 3))
links = [(HKP.Value('HEAD'), HKP.Value('NECK')), (HKP.Value('NECK'), HKP.Value('CHEST')),
         (HKP.Value('CHEST'), HKP.Value('RIGHT_HIP')
          ), (HKP.Value('CHEST'), HKP.Value('LEFT_HIP')),
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
    """_summary_

    Args:
        images (_type_): _description_
        annotations (_type_): _description_
        it (_type_): _description_
        links (_type_): _description_
        colors (_type_): _description_

    Returns:
        _type_: _description_
    """
    for cam_id, image in images.items():
        deteccoes = 0  # Detections in each frame
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
                    cv2.line(image, parts[begin],
                             parts[end], color=color, thickness=4)
            for center in parts.values():
                cv2.circle(image, center=center, radius=4,
                           color=(255, 255, 255), thickness=-1)

        if deteccoes < 10:
            juntas[cam_id] -= deteccoes
            # perdidas[cam_id] = 0
        else:
            perdidas[cam_id] += 15 - deteccoes

    return juntas, perdidas


def render_skeletons_3d(ax, skeletons, links, colors, juntas_3d, perdidas_3d):
    """_summary_

    Args:
        ax (_type_): _description_
        skeletons (_type_): _description_
        links (_type_): _description_
        colors (_type_): _description_
        juntas_3d (_type_): _description_
        perdidas_3d (_type_): _description_

    Returns:
        _type_: _description_
    """
    deteccoes_3d = 0
    skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
    # print(skeletons_pb)

    for skeleton in skeletons_pb.objects:
        parts = {}
        for part in skeleton.keypoints:
            deteccoes_3d += 1
            juntas_3d += 1
            parts[part.id] = (
                part.position.x, part.position.y, part.position.z)
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

    # ???
    # Por que 10 e 15?
    if deteccoes_3d < 10:
        juntas_3d -= deteccoes_3d
    else:
        perdidas_3d += 15 - deteccoes_3d
    return juntas_3d, perdidas_3d


def send_information(skeletons):
    """_summary_

    Args:
        skeletons (_type_): _description_
    """
    skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='Receive_information')
    for skeleton in skeletons_pb.objects:
        parts = {}
        for part in skeleton.keypoints:
            parts[part.id] = (
                part.position.x, part.position.y, part.position.z)
            channel.basic_publish(exchange='', routing_key='Receive_information', body=json.dumps(
                {'dict': skeletons}).encode('utf-8'))

        # print("Enviado")
    connection.close()


def place_images(output_image, images, x_offset=0, y_offset=0):
    """_summary_

    Args:
        output_image (_type_): _description_
        images (_type_): _description_
        x_offset (int, optional): _description_. Defaults to 0.
        y_offset (int, optional): _description_. Defaults to 0.
    """
    h, w = images[0].shape[0:2]
    output_image[0 + y_offset:h + y_offset, 0 +
                 x_offset:w + x_offset, :] = images[0]

    output_image[0 + y_offset:h + y_offset, w +
                 x_offset:2 * w + x_offset, :] = images[1]

    output_image[h + y_offset:2 * h + y_offset,
                 0 + x_offset:w + x_offset, :] = images[2]

    output_image[h + y_offset:2 * h + y_offset, w +
                 x_offset:2 * w + x_offset, :] = images[3]


with open('keymap.json', 'r') as f:
    keymap = json.load(f)
options = load_options(print_options=False)

if not os.path.exists(options.folder):
    log.critical("Folder '{}' doesn't exist", options.folder)

with open('gestures.json', 'r') as f:
    gestures = json.load(f)

    # Sus ordered
    gestures = OrderedDict(sorted(gestures.items(), key=lambda kv: int(kv[0])))

#parser
parser = argparse.ArgumentParser(
    description='Utility to capture a sequence of images from multiples cameras')
parser.add_argument('--person', '-p', type=int,
                    required=True, help='ID to identity person')
parser.add_argument('--gesture', '-g', type=int,
                    required=True, help='ID to identity gesture')
args = parser.parse_args()

person_id = args.person
gesture_id = args.gesture

if str(gesture_id) not in gestures:
    log.critical("Invalid GESTURE_ID: {}. \nAvailable gestures: {}", gesture_id,
                 json.dumps(gestures, indent=2))

if person_id < 1 or person_id > 999:
    log.critical(
        "Invalid PERSON_ID: {}. Must be between 1 and 999.", person_id)

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
        2 * options.cameras[0].config.image.resolution.width,
        3)

full_image = np.zeros(size, dtype=np.uint8)

video_loader = MultipleVideoLoader(video_files)

# load annotations
annotations = {}
for cam_id, filename in json_files.items():
    with open(filename, 'r') as f:
        annotations[cam_id] = json.load(f)['annotations']

# load localizations
with open(json_locaizations_file, 'r') as f:
    localizations = json.load(f)['localizations']

plt.ioff()
fig = plt.figure(figsize=(5, 5))
ax = Axes3D(fig)

output_file = 'p{:03d}g{:02d}_output.mp4'.format(person_id, gesture_id)

def video_writer(fps=60.0,width=1288,height=728):
        
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    #arquivo de vídeo que será preenchido com imagens
    vid = cv2.VideoWriter('record_screen.avi', fourcc, fps, (width, height))
    return vid
vid = video_writer()
##Quantidade de ciclos analisados para se normalizar as medições no final!!!!!####
# int(input("Número de ciclos desejado para normalização:"))
quant_de_ciclos_desejado = 4

#Comentado por Deivid em 09/05/2023 para teste pois o arquivo "Dados_medicoes.txt" não existe
'''##Leitura dos dados reais medidos##
dados_da_medicao_real = []
# Leitura dos dados medidos
with open(options.folder + "/Dados_medicoes.txt", "r+") as file_read_information:
    for linha in file_read_information.readlines():
        x = linha.split()
        dados_da_medicao_real.append(x[len(x) - 2])

# Deveria ser um dicio???
altura_real = dados_da_medicao_real[0]
idade = dados_da_medicao_real[1]
massa = dados_da_medicao_real[2]
sexo = float(dados_da_medicao_real[3])
comprimento_passo_real_medido = float(dados_da_medicao_real[4])
Stance_real = float(dados_da_medicao_real[5])
Swing_real = float(dados_da_medicao_real[6])
dist_dos_pes_inicial = float(dados_da_medicao_real[7])
altura_quadril = float(dados_da_medicao_real[8])'''

# Digitado por Deivid para teste em 09/05/2023. É necessario um arquivo que é atualmente desconhecido?
altura_real = 1.87
idade = 22
massa = 84
sexo = 'M'
comprimento_passo_real_medido = 1
Stance_real = 1
Swing_real = .5
dist_dos_pes_inicial = 0
altura_quadril = 1

b = a = altura_quadril / 2
#pow??? mudado para **
B = altura_quadril**2 - (a**2 + b**2)
A = -2 * b * altura_quadril
if (B / A) < 1:
    angulo_real_joelho_esquerdo = math.degrees(math.acos(B / A))
else:
    angulo_real_joelho_esquerdo = 0

angulo_real_joelho_esquerdo = (
    180 - angulo_real_joelho_esquerdo)  # Está como no livro!!!!#

# ???
# Muitas variaveis soltas. Codigo extremamente sujo. Necessario refatorar.

# [0, 0, 0, 0]           # Lista de juntas detectadas em cada câmera
x, y = [], []
a = b = i = 0
r = 1
k = 0

juntas = [0] * 4
perdidas = [0] * 4
juntas_3d = perdidas_3d = 0
it_frames = 0
Velocidade_no_instante = 0
picos_distancia = [0]
average_height = [0]
tempo_inicial = time.time()
aux_tempo = 0
dist_do_chao = [0]
tempo_anterior = 0
perna_esquerda = [0]
perna_esquerda_aux1 = perna_esquerda_aux2 = 0
perna_direita = [0]
distance_feet = [0, 0, 0, 1]
distance_feet_2 = [1]
distance_feet_3 = [1]  # Plano XY
contador_numero_de_passos = 0
aceleracao = [0]
classifier = 0.0
gait_cycle_dist_feet_percent = [0]
quant_de_ciclos = 0  # Mede a quantidade de ciclos em cada uma das caminhadas
aux_quantidade_de_ciclos = []
instante = [0]
aux_velocidade_instante = [0]
instante_pico = [0]
tempo_passo = [0]
tempo_suporte_duplo = [0]
comprimento_passo_medido = [0]
comprimento_stance = [1, 1]
comprimento_swing = [1, 1]
largura_da_passada = [1]
largura_media = 0
aux_largura_da_passada = 0
aux_angulo = [0]
aux_angulo_gait_cycle = [0]
angulo = 0
cadencia = 0
flexion_left_knee_angle = [1]
flexion_right_knee_angle = [1]
aux_left_knee_angle = 0
aux_right_knee_angle = 0
coxa_perna_esquerda = [0]
velocidade_angular_flexion_right_knee_angle = [0]
velocidade_angular_flexion_left_knee_angle = [0]
velocidade_media = 0
ang_ext_quadril_direito = [0]
ang_ext_quadril_esquerdo = [0]
vetor_normal = [0]
aux_ang_ext_quadril = 0
aux_vetor_normal = 0
aux_flexion_left_knee = 0
simetria_comprimento_passo = [0]
t = [0]
data_json = {'dados': [0]}
movimento = 0  # Time up:0, Em círculos:1, Em linha reta:2, Elevação excessiva:3, Assimétrica:4 e Circundação do pé:5
altura_pe_esquerdo = 0
altura_pe_direito = 0
altura_calcanhar = 0.135 #??? PQ 0.135???
ponto_tornozelo_direito = []
ponto_tornozelo_esquerdo = []
slide = 0  # input("Digite um valor para o silde: 0, 2 ou 4 ")
slide_result = Parameter.slide_gait_cycle(slide)
array_coordenadas = []  # Array de coordenadas do esqueleto
matrix_coordenadas = []
aux_movimento = [movimento]

# Aqui começa a análise dos vídeos para cada frame

for it_frames in range(video_loader.n_frames()):
    video_loader.load_next()

    # dois time.time???
    tempo_anterior = time.time()
    aux_tempo = time.time()  # atualiza o instante de tempo entre os frames

    frames = video_loader[it_frames]
    if frames is not None:
        juntas, perdidas = render_skeletons(
            frames, annotations, it_frames, links, colors)
        frames_list = [frames[cam] for cam in sorted(frames.keys())]
        place_images(full_image, frames_list)

    ax.clear()
    ax.view_init(azim=28, elev=32)
    ax.set_xlim(-1.5, 0)
    ax.set_ylim(-3.0, 3.0)
    ax.set_zlim(-0.25, 1.5)

    ax.set_xticks(np.arange(-1.5, 0.5, 0.5))
    ax.set_yticks(np.arange(-5.0, 2.0, 0.5))
    ax.set_zticks(np.arange(0, 1.75, 0.5))

    ax.set_xlabel('X', labelpad=20)
    ax.set_ylabel('Y', labelpad=10)
    ax.set_zlabel('Z', labelpad=5)
    juntas_3d, perdidas_3d = render_skeletons_3d(
        ax, localizations[it_frames], links, colors, juntas_3d, perdidas_3d)
    perdas_no_3d = Parameter.perdas_3d(
        ax, localizations[it_frames], links, colors)
    i = i + 1
    if perdas_no_3d is None:
        perdas_no_3d = 100

    y.append(perdas_no_3d)
    x.append(i)
    aux_localizations = []

    average_height.append(
        Parameter.altura_da_pessoa(localizations[it_frames]))
    perna_esquerda_aux1, perna_esquerda_aux2, aux_left_knee_angle, aux_flex_quadril_ang = Parameter.left_leg(
        localizations[it_frames])
    perna_esquerda.append(perna_esquerda_aux1)
    perna_direita_aux, dist_do_chao_aux, aux_largura_da_passada, aux_right_knee_angle, altura_pe_direito, altura_pe_esquerdo, ponto_tornozelo_direito, ponto_tornozelo_esquerdo = Parameter.right_leg(
        localizations[it_frames])
    perna_direita.append(perna_direita_aux)
    dist_do_chao.append(dist_do_chao_aux)  # Altura media dos pes

    if ((altura_pe_esquerdo >= altura_calcanhar >= altura_pe_direito) or (
            altura_pe_esquerdo <= altura_calcanhar <= altura_pe_direito)):
        flexion_right_knee_angle.append(aux_right_knee_angle)
        # Armazena os valores dos angulos do joelho esquerdo
        flexion_left_knee_angle.append(aux_left_knee_angle)
        ang_ext_quadril_direito.append(aux_ang_ext_quadril)
        ang_ext_quadril_esquerdo.append(aux_flex_quadril_ang)

    largura_da_passada.append(float(aux_largura_da_passada))

    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    view_3d = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    display_image = cv2.resize(full_image, dsize=(0, 0), fx=0.5, fy=0.5)
    hd, wd, _ = display_image.shape
    hv, wv, _ = view_3d.shape

    display_image = np.hstack(
        [display_image, 255 * np.ones(shape=(hd, wv, 3), dtype=np.uint8)])
    display_image[int((hd - hv) / 2):int((hd + hv) / 2), wd:, :] = view_3d

    # Velocidade angular dos ângulos medidos
    intervalo_de_tempo = (time.time() - tempo_inicial)
    velocidade_angular_flexion_right_knee_angle.append(Parameter.velocidade_angular(
        flexion_right_knee_angle[len(flexion_right_knee_angle) - 1], intervalo_de_tempo))

    if SkeletonsCoord.joint_coord(localizations[it_frames], 12) and SkeletonsCoord.joint_coord(localizations[it_frames],
                                                                                               15):
        right_foot = SkeletonsCoord.joint_coord(localizations[it_frames], 12)
        left_foot = SkeletonsCoord.joint_coord(localizations[it_frames], 15)
        distance_feet.append(np.sqrt((right_foot[0] - left_foot[0]) ** 2 + (
            right_foot[1] - left_foot[1]) ** 2 + (right_foot[2] - left_foot[2]) ** 2))
        # Diferença entre as alturas dos pés
        distance_feet_2.append(right_foot[1] - left_foot[1])
        distance_feet_3.append(
            np.sqrt((right_foot[1] - left_foot[1]) ** 2))  # Plano XY
        instante.append(time.time() - tempo_inicial)
        # tempo_inicial
        tempo_total = time.time() - tempo_inicial
        tempo_total_em_min = tempo_total / 60
        cadencia = contador_numero_de_passos / tempo_total_em_min
        velocidade_media = sum(distance_feet_3) / tempo_total
        array_coordenadas, nome_das_coordenadas = Parameter.Array_coordenadas(
            localizations[it_frames])
        if len(matrix_coordenadas) == 0:
            matrix_coordenadas = array_coordenadas
        matrix_coordenadas = np.vstack([matrix_coordenadas, array_coordenadas])

        if len(distance_feet) >= 3:
            if (distance_feet[len(distance_feet) - 1]) < (distance_feet[len(distance_feet) - 2]):
                if distance_feet[len(distance_feet) - 2] > distance_feet[len(distance_feet) - 3]:
                    if distance_feet[len(distance_feet) - 2] >= (Swing_real or Stance_real):
                        contador_numero_de_passos = contador_numero_de_passos + \
                            1  # Conta quantos passos foram dados
                        picos_distancia.append(
                            distance_feet[len(distance_feet) - 2])
                        instante_pico.append(instante[len(instante) - 1])
                        i = len(picos_distancia) - 1
                        xs = ponto_tornozelo_direito[0]
                        ys = ponto_tornozelo_direito[1]
                        zs = ponto_tornozelo_direito[2]
                        ax.scatter(xs, ys, zs, marker='^')

                        # print(picos_distancia)

                        if i % 2 == 0:
                            comprimento_swing.append(picos_distancia[i])
                            r = (comprimento_swing[-1]) / \
                                (comprimento_stance[-1])
                            simetria_comprimento_passo.append(r)

                        else:
                            comprimento_stance.append(picos_distancia[i])

            if (contador_numero_de_passos % 2) == 0:
                quant_de_ciclos = contador_numero_de_passos / 2
                comprimento_passo_medido.append(
                    (picos_distancia[contador_numero_de_passos - 1] + picos_distancia[
                        contador_numero_de_passos - 2]))  # Conta cada passada dada

            aux_quantidade_de_ciclos.append(quant_de_ciclos)
            if (quant_de_ciclos % quant_de_ciclos_desejado) == 0 and quant_de_ciclos != 0:
                # Verfica a mudança da quantidade de ciclos
                if aux_quantidade_de_ciclos[-1] != aux_quantidade_de_ciclos[-2]:
                    # ???
                    # absolute path desconhecido
                    with open(
                            '/home/julian/docker/Pablo/CICLOS_v4/{}/{}/Coordenadas_das_juntas_de_todos_para_validacao_{}_ciclos_{}.csv'.format(
                                CAPTURA, quant_de_ciclos_desejado, quant_de_ciclos_desejado, CAPTURA),
                            'a') as csvfile:
                        filewriter = csv.writer(csvfile, delimiter=',',
                                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        media_das_coordenadas = np.mean(
                            matrix_coordenadas, axis=0)
                        media_das_coordenadas = np.concatenate(
                            (media_das_coordenadas, aux_movimento), axis=None)

                        media_das_coordenadas = []  # del media_das_coordenadas[:]
                        matrix_coordenadas = []  # del matrix_coordenadas[:]

    aux_angulo.append(Parameter.angulo_caminhada_real(
        perna_esquerda_aux1, perna_direita_aux, distance_feet_2[len(distance_feet_2) - 1]))

    aux_ang_ext_quadril, aux_vetor_normal, aux_ponto_peito = (
        Parameter.ang_plano_torax(localizations[it_frames]))
    vetor_normal.append(aux_vetor_normal)
    X, Y, Z = np.meshgrid(aux_vetor_normal[0]), np.meshgrid(
        aux_vetor_normal[1]), np.meshgrid(aux_vetor_normal[2])
    u = X
    v = Y
    w = Z
    ax.quiver(aux_ponto_peito[0], aux_ponto_peito[1],
              aux_ponto_peito[2], u, v, w, length=1, color='r', normalize=True)

    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    view_3d = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    display_image = cv2.resize(full_image, dsize=(0, 0), fx=0.5, fy=0.5)
    hd, wd, _ = display_image.shape
    hv, wv, _ = view_3d.shape

    display_image = np.hstack(
        [display_image, 255 * np.ones(shape=(hd, wv, 3), dtype=np.uint8)])
    display_image[int((hd - hv) / 2):int((hd + hv) / 2), wd:, :] = view_3d

    aux_flexion_left_knee = Parameter.flexion_left_knee(
        localizations[it_frames])
    # Ângulo da coxa do joelho esquerdo !!!!!
    coxa_perna_esquerda.append(aux_flexion_left_knee)

    aux_velocidade_instante.append(Velocidade_no_instante)
    cv2.putText(display_image,
                "Angulo de caminhada: %.3f graus" % aux_angulo[it_frames] + " +- %.3f" % (statistics.mean(
                    aux_angulo) - aux_angulo[it_frames]), (1300, 30), cv2.FONT_HERSHEY_SIMPLEX, .4, (100, 00, 10), 1,
                cv2.LINE_AA)
    cv2.imshow('', display_image)
    Velocidade_no_instante = (
        abs(distance_feet_2[len(distance_feet_2) - 1]) / (time.time() - aux_tempo))
    cv2.putText(display_image,
                "Velocidade da caminhada: %.3f m/s " % Velocidade_no_instante + " +- %.3f" % (statistics.mean(
                    aux_velocidade_instante) - Velocidade_no_instante), (1300, 45), cv2.FONT_HERSHEY_SIMPLEX, .4,
                (100, 00, 10), 1, cv2.LINE_AA)
    cv2.imshow('', display_image)
    cv2.putText(display_image, "Stance medido: %.3f m " % Stance_real,
                (1300, 60), cv2.FONT_HERSHEY_SIMPLEX, .4, (100, 00, 10), 1, cv2.LINE_AA)
    cv2.imshow('', display_image)
    cv2.putText(display_image, "Swing medido: %.3f m " % Swing_real,
                (1300, 75), cv2.FONT_HERSHEY_SIMPLEX, .4, (100, 00, 10), 1, cv2.LINE_AA)
    cv2.imshow('', display_image)
    cv2.putText(display_image,
                "Stance/Swing: %.3f m" % abs(distance_feet_2[len(distance_feet_2) - 1]) + " +- %.3f" % abs(
                    (distance_feet_2[len(distance_feet_2) - 1]) - Stance_real), (1300, 90), cv2.FONT_HERSHEY_SIMPLEX,
                .4, (100, 00, 10), 1, cv2.LINE_AA)
    cv2.imshow('', display_image)
    cv2.putText(display_image, "Angulo de flexao do joelho da perna esquerda: %.3f graus" % (
        flexion_left_knee_angle[-1]), (1300, 105), cv2.FONT_HERSHEY_SIMPLEX, .4, (100, 00, 10), 1, cv2.LINE_AA)
    cv2.imshow('', display_image)
    cv2.putText(display_image, "Angulo de flexao do joelho da perna direita: %.3f graus" % (
        flexion_right_knee_angle[-1]), (1300, 120), cv2.FONT_HERSHEY_SIMPLEX, .4, (100, 00, 10), 1, cv2.LINE_AA)
    cv2.imshow('', display_image)
    cv2.putText(display_image, "Distancia entre os pes: %.3f m" % distance_feet[len(
        distance_feet) - 1], (1300, 135), cv2.FONT_HERSHEY_SIMPLEX, .4, (100, 00, 10), 1, cv2.LINE_AA)
    cv2.imshow('', display_image)
    Parameter.marca_frame(
        contador_numero_de_passos=contador_numero_de_passos, frame=display_image)
    # cv2.putText(display_image, "Movimento reconhecido como: %s m" % Parameter.rede_neural(velocidade_media,
    # statistics.mean(comprimento_passo_medido),statistics.mean(largura_da_passada),statistics.mean(
    # simetria_comprimento_passo),cadencia), (1300,175),cv2.FONT_HERSHEY_SIMPLEX, .4, (100,00,10),1, cv2.LINE_AA)
    # cv2.imshow('', display_image)

    data_json['dados'].append({
        'frame': '%i' % it_frames,
        'flexion angle right knee': '%.2f' % flexion_right_knee_angle[len(flexion_right_knee_angle) - 1],
        'flexion angle left knee': '%.2f' % flexion_left_knee_angle[len(flexion_left_knee_angle) - 1],
        'altura medida (m)': '%.3f' % average_height[len(average_height) - 1],
        'angulo ext do quadril direito': '%.3f' % aux_ang_ext_quadril,
        'largura da passada': '%.3f' % float(aux_largura_da_passada),
        'angulo de caminhada': '%.3f' % aux_angulo[len(aux_angulo) - 1],
        'velocidade no instante (m/s)': '%.3f' % Velocidade_no_instante
    })

    vid.write(display_image)

    ##MANDA OS DADOS PELA REDE LOCAL!###
    # send_information(localizations[it_frames])
    # key = cv2.waitKey(1)
    if cv2.waitKey(57) & 0xFF == ord('q'):
        break

Parameter.write_json(data_json)

ang_ext_quadril_direito = ang_ext_quadril_direito[1:]
distance_feet = distance_feet[1:]  # Retira o primeiro elemento
flexion_left_knee_angle = flexion_left_knee_angle[1:]
flexion_right_knee_angle = flexion_right_knee_angle[1:]

maior_elemento_distancia_entre_pes_eixo_x = (max(distance_feet_2))

# Retira o primeiro elemento
comprimento_stance = comprimento_stance[1:]  
comprimento_swing = comprimento_swing[1:]
largura_da_passada = largura_da_passada[1:]
distance_feet = distance_feet[1:]
distance_feet_2 = distance_feet_2[1:]
instante = instante[1:]
tempo_passo = tempo_passo[2:]

if len(picos_distancia)% 2 == 0:
    for j in range(len(picos_distancia) - 1):
        tempo_passo.append(instante_pico[j + 1] - instante_pico[j])
    for j in range(len(picos_distancia) - 2, 2):
        tempo_suporte_duplo.append(instante_pico[j + 2] - instante_pico[j])
else:
    for j in range(len(picos_distancia) - 1):
        tempo_passo.append(instante_pico[j + 1] - instante_pico[j])
    for j in range(len(picos_distancia) - 2, 2):
        tempo_suporte_duplo.append(instante_pico[j + 2] - instante_pico[j])

for i in range(len(flexion_left_knee_angle)):
    if flexion_left_knee_angle[i] == 180:
        flexion_left_knee_angle[i] = flexion_left_knee_angle[i - 1]

for i in range(0, len(tempo_passo)):
    aceleracao.append((picos_distancia[i] / (pow(tempo_passo[i], 2))))

h = list(range(1, len(tempo_passo) + 1))

print("Meio comprimento de passo médio: %.3f m" %
      statistics.mean(picos_distancia))

maior_passo_medido = picos_distancia[0] + picos_distancia[1]
print("Maior comprimento de passo: %.3f m" % maior_passo_medido)

for cam_id in range(4):
    porcentagem = (perdidas[cam_id] / juntas[cam_id]) * 100
    log.info("cam{}: Juntas detectadas: {} | Perdidas: {} |  {:.2f} %".format(
        cam_id, juntas[cam_id], perdidas[cam_id], porcentagem))

porcentagem_3d = (perdidas_3d / juntas_3d) * 100
log.info("Juntas detectadas [Serviço 3d]: {} | Perdidas: {} |  {:.2f} %".format(
    juntas_3d, perdidas_3d, porcentagem_3d))

log.info('Exiting')
soma_perdas = sum(y)
tempo_total = time.time() - tempo_inicial
print("Tempo de suporte duplo: %.4f s" % (0.2 * tempo_total))
velocidade_media = sum(distance_feet) / tempo_total
print("Velocidade média: %.3f m/s " % velocidade_media)
perda_media = soma_perdas / len(x)
print("Perda média do 3D: %5.2f" % perda_media +
      " +- %5.3f" % statistics.pstdev(y) + " %")
variancia = statistics.variance(y)
print("Variância de %5.3f " % variancia + " % no 3D")
print("Número de passos: %d " % contador_numero_de_passos)

tempo_total = sum(tempo_passo)  # Tempo em segundos
tempo_total_em_min = tempo_total / 60
cadencia = contador_numero_de_passos / tempo_total_em_min
print("Cadência (passos/min): %.3f " % cadencia)
print("Tempo total: %.3f s " % tempo_total)

# Muitos plots???
Plota_graficos.Plot.plota_grafico_perdas(y)
Plota_graficos.Plot.plota_grafico_distance_feet(instante, distance_feet)
Plota_graficos.Plot.plota_grafico_tempo_de_passo(
    h, tempo_passo, 'Passo', 'Tempo de passo(s)', 'Tempo de Passos')
angulo = Parameter.angulo_caminhada(
    perna_direita, perna_esquerda, picos_distancia, altura_quadril)

largura_media = statistics.mean(largura_da_passada)

title = 'Ângulo de abertura entre as pernas por número de amostras'
Plota_graficos.Plot.plota_angulo_medido(aux_angulo, title)
coxa_perna_esquerda = Parameter.retira_primeiro_elemento(coxa_perna_esquerda)
title = 'Ângulo da coxa do joelho esquerdo durante a caminhada'
Plota_graficos.Plot.plota_angulo_medido(coxa_perna_esquerda, title)
flexion_left_knee_angle = Parameter.retira_primeiro_elemento(
    flexion_left_knee_angle)
title = 'Ângulo de flexão joelho esquerdo durante a caminhada'
Plota_graficos.Plot.plota_angulo_medido(flexion_left_knee_angle, title)
flexion_right_knee_angle = Parameter.retira_primeiro_elemento(
    flexion_right_knee_angle)
title = 'Ângulo de flexão joelho direito durante a caminhada'
Plota_graficos.Plot.plota_angulo_medido(flexion_right_knee_angle, title)
simetria_comprimento_passo = Parameter.retira_primeiro_elemento(
    simetria_comprimento_passo)
title = 'Simetria do comprimento de passo durante a caminhada'
Plota_graficos.Plot.plota_simetria(simetria_comprimento_passo, title)
ang_ext_quadril_direito = Parameter.retira_primeiro_elemento(
    ang_ext_quadril_direito)
title = 'Ângulo da extensão do quadril direito durante a caminhada'
Plota_graficos.Plot.plota_angulo_medido(ang_ext_quadril_direito, title)

title = 'Ângulo de abertura entre as pernas por ciclo'
aux_angulo = Parameter.normaliza_vetor(
    aux_angulo, quant_de_ciclos, quant_de_ciclos_desejado, 70)
Plota_graficos.Plot.plota_angulo_medido_normalizado(aux_angulo, title)

title = 'Ângulo de flexão joelho esquerdo no ciclo'
flexion_left_knee_angle = Parameter.normaliza_vetor(
    flexion_left_knee_angle, quant_de_ciclos, quant_de_ciclos_desejado,
    70)  # pico do sinal em 70 % do ciclo para a flexão
Plota_graficos.Plot.plota_angulo_medido_normalizado(flexion_left_knee_angle, title)

title = 'Ângulo de flexão joelho direito no ciclo'
flexion_right_knee_angle = Parameter.normaliza_vetor(
    flexion_right_knee_angle, quant_de_ciclos, quant_de_ciclos_desejado, 70)
Plota_graficos.Plot.plota_angulo_medido_normalizado(flexion_right_knee_angle, title)

title = 'Ângulo de extensão do quadril direito por ciclo'
right_extension_hip_angle = Parameter.normaliza_vetor(
    ang_ext_quadril_direito, quant_de_ciclos, quant_de_ciclos_desejado, 80)
Plota_graficos.Plot.plota_angulo_medido_normalizado(
    right_extension_hip_angle, title)

title = 'Ângulo de extensão do quadril esquerdo por ciclo'
left_extension_hip_angle = Parameter.normaliza_vetor(
    ang_ext_quadril_esquerdo, quant_de_ciclos, quant_de_ciclos_desejado, 80)
Plota_graficos.Plot.plota_angulo_medido_normalizado(left_extension_hip_angle, title)

title = 'Velocidade angular flexão do joelho direito normalizado por ciclo'
velocidade_angular_flexion_right_knee_angle = Parameter.normaliza_vetor(
    velocidade_angular_flexion_right_knee_angle, quant_de_ciclos, quant_de_ciclos_desejado, 50)
Plota_graficos.Plot.plota_angulo_medido_normalizado(
    velocidade_angular_flexion_right_knee_angle, title)

Plota_graficos.Plot.plota_grafico(
    ang_ext_quadril_esquerdo, "Ângulo de extensão do quadril esquerdo ")
Plota_graficos.Plot.plota_grafico(aceleracao, "Aceleração [m.s-²]")

Parameter.file_maker(cam_id, juntas, perdidas, juntas_3d, perdidas_3d, average_height, idade, porcentagem,
                      porcentagem_3d, perda_media, variancia, y, x, perna_esquerda, perna_direita, maior_passo_medido,
                      tempo_total, velocidade_media, cadencia, contador_numero_de_passos, tempo_total_em_min,
                      dist_do_chao, comprimento_passo_real_medido, Stance_real,
                      Swing_real, distance_feet, dist_dos_pes_inicial, picos_distancia, comprimento_passo_medido,
                      comprimento_swing, comprimento_stance, aux_angulo, altura_quadril, coxa_perna_esquerda,
                      angulo_real_joelho_esquerdo, comprimento_passo_real_medido, flexion_left_knee_angle,
                      simetria_comprimento_passo, largura_da_passada, ang_ext_quadril_direito)
Parameter.erro_medio_da_caminhada(comprimento_passo_real_medido, Stance_real, Swing_real, distance_feet,
                                   dist_dos_pes_inicial, picos_distancia, comprimento_passo_medido, comprimento_swing,
                                   comprimento_stance, aux_angulo, altura_quadril,
                                   perna_direita, coxa_perna_esquerda, angulo_real_joelho_esquerdo,
                                   flexion_left_knee_angle, flexion_right_knee_angle, simetria_comprimento_passo,
                                   largura_da_passada, left_extension_hip_angle, right_extension_hip_angle)
classifier = Parameter.fuzzy(velocidade_media, cadencia, largura_media,
                              comprimento_passo_medido, comprimento_passo_real_medido, dist_dos_pes_inicial)

if classifier >= 5:
    print("O movimento foi realizado de forma correta !")
    #movimento = 0
else:
    print("O movimento foi realizado de forma errada")
    #movimento = 1

vid.release()
cv2.destroyAllWindows()
