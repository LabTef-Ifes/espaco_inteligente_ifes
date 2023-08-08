# -*- coding: utf-8 -*-
import json
import numpy as np
import math
from collections import defaultdict
'''
HumanKeypoints
Models keypoints present in the human body.

| Name                   | Number | Description |
| ---------------------- | ------ | ----------- |
| UNKNOWN_HUMAN_KEYPOINT | 0      |             |
| HEAD                   | 1      |             |
| NOSE                   | 2      |             |
| NECK                   | 3      |             |
| RIGHT_SHOULDER         | 4      |             |
| RIGHT_ELBOW            | 5      |             |
| RIGHT_WRIST            | 6      |             |
| LEFT_SHOULDER          | 7      |             |
| LEFT_ELBOW             | 8      |             |
| LEFT_WRIST             | 9      |             |
| RIGHT_HIP              | 10     |             |
| RIGHT_KNEE             | 11     |             |
| RIGHT_ANKLE            | 12     |             |
| LEFT_HIP               | 13     |             |
| LEFT_KNEE              | 14     |             |
| LEFT_ANKLE             | 15     |             |
| RIGHT_EYE              | 16     |             |
| LEFT_EYE               | 17     |             |
| RIGHT_EAR              | 18     |             |
| LEFT_EAR               | 19     |             |
| CHEST                  | 20     |             |
'''


class Skeleton:
    """Classe que representa um esqueleto. Guarda os pontos do esqueleto em um dicionário, onde a chave é o id do ponto e o valor é um objeto da classe Joint.
    Classe usada exclusivamente para o cálculo de posições, ângulos e distâncias entre os pontos do esqueleto."""

    class Joint:
        def __init__(self, id, x, y, z):
            """Classe que representa um ponto do esqueleto. Guarda seu id, nome e coordenadas x,y,z.

            Args:
                id (str): id segundo a biblioteca
                x (float): ponto cartesiano x descrito no json
                y (float): ponto cartesiano y descrito no json
                z (float): ponto cartesiano z descrito no json
            """
            self.id = id
            self.name = Calculate.human_parts_id[id]
            self.x = x
            self.y = y
            self.z = z

        def __str__(self):
            return f'Joint: {self.name} | x: {self.x:.4f} | y: {self.y:.4f} | z: {self.z:.4f}'
        __repr__ = __str__

    def __init__(self, frame_dict: dict):
        """Recebe um dicionario que possui as chaves "objects" e "keypoints" e salva um objeto com os dados do esqueleto no frame.

        Args:
            frame_dict (dict): dicionario que contém "objects" com seus keypoints
        """
        self.objects: list[dict] = frame_dict[
            'objects']  # Lista de objetos(pessoas) no frame
        # Lista os keypoints de todos os esqueletos presentes
        self.keypoints: list[dict] = [human['keypoints']
                                      for human in self.objects]
        self.joints: dict[str, Skeleton.Joint] = self.read_joints()

    def read_joints(self):
        """Lê os pontos do esqueleto e os salva em um dicionário

        Returns:
            dict[str,Skeleton.Joint]: Dicionário com os pontos do esqueleto
        """
        joints: dict[str, Skeleton.Joint] = {}
        for human in self.objects:
            for keypoint in human['keypoints']:
                position = keypoint['position']
                joints[keypoint['id']] = Skeleton.Joint(
                    keypoint['id'], position['x'], position['y'], position['z'])
        return joints


class Calculate:
    human_parts_id: dict = {
        '0': 'UNKNOWN_HUMAN_KEYPOINT',
        '1': 'HEAD',
        '2': 'NOSE',
        '3': 'NECK',
        '4': 'RIGHT_SHOULDER',
        '5': 'RIGHT_ELBOW',
        '6': 'RIGHT_WRIST',
        '7': 'LEFT_SHOULDER',
        '8': 'LEFT_ELBOW',
        '9': 'LEFT_WRIST',
        '10': 'RIGHT_HIP',
        '11': 'RIGHT_KNEE',
        '12': 'RIGHT_ANKLE',
        '13': 'LEFT_HIP',
        '14': 'LEFT_KNEE',
        '15': 'LEFT_ANKLE',
        '16': 'RIGHT_EYE',
        '17': 'LEFT_EYE',
        '18': 'RIGHT_EAR',
        '19': 'LEFT_EAR',
        '20': 'CHEST'
    }
    human_parts_name: dict = {
        'UNKNOWN_HUMAN_KEYPOINT': 0,
        'HEAD': 1,
        'NOSE': 2,
        'NECK': 3,
        'RIGHT_SHOULDER': 4,
        'RIGHT_ELBOW': 5,
        'RIGHT_WRIST': 6,
        'LEFT_SHOULDER': 7,
        'LEFT_ELBOW': 8,
        'LEFT_WRIST': 9,
        'RIGHT_HIP': 10,
        'RIGHT_KNEE': 11,
        'RIGHT_ANKLE': 12,
        'LEFT_HIP': 13,
        'LEFT_KNEE': 14,
        'LEFT_ANKLE': 15,
        'RIGHT_EYE': 16,
        'LEFT_EYE': 17,
        'RIGHT_EAR': 18,
        'LEFT_EAR': 19,
        'CHEST': 20
    }

    class Vector:
        """Um segmento do corpo pode ser tratado como um vetor, com origem no ponto A e destino no ponto B. Assim, usamos álgebra para obter sua magnitude e ângulo criando vetores entre dois pontos do corpo.
        """

        def __init__(self, point_a, point_b):
            """Cria um vetor entre dois pontos"""
            self.point_a = point_a
            self.x = point_b.x - point_a.x
            self.y = point_b.y - point_a.y
            self.z = point_b.z - point_a.z

        @property
        def vector(self):
            return np.array([self.x, self.y, self.z])

        @property
        def magnitude(self):
            return np.linalg.norm(self.vector)

        def calculate_angle(self, vector):
            """Calcula o ângulo entre dois vetores usando produto interno

            Args:
                vector (Vector): Outro vetor com o mesmo ponto de origem

            Returns:
                float: angulo em graus
            """
            #assert self.point_a == vector.point_a, "Os vetores devem ter o mesmo ponto de origem"
            return math.degrees(math.acos(np.dot(self.vector, vector.vector)/(self.magnitude*vector.magnitude)))

        # Define a operação //
        def __floordiv__(self, other):
            return self.calculate_angle(other)

    def __init__(self, file3d):
        # Dicionario para guardar as informações que serão plotadas posteriormente
        self.plot_data: dict = defaultdict(list)
        self.file3d = file3d
        self.data = self.read_json()
        self.frames = len(self.data)
        self.dt = 1/6 # Tempo entre cada frame. inverso de frames por segundo

    def run_frames(self):
        """Passa por todos os frames, calculando as informações necessárias para o plot usando a classe Skeleton para guardar as informações. Ao final, chama a função que plota os dados"""
        for i, frame_info in enumerate(self.data):
            self._calculate_angle('13','14','15', frame_info)

    def _calculate_angle(self, first, central, last,frame:int):
        """Calcula o ângulo entre tres pontos. 
        Função usada por outras funções para calcular ângulos entre segmentos do corpo. 
        Recebe os ids das partes do corpo em string.

        Args:
            first (str): _description_
            central (str): _description_
            last (str): _description_

        Returns:
            float: ângulo em graus
        """
        try:
            first_joint:Skeleton.Joint = Skeleton(frame).joints[first]
            central_joint:Skeleton.Joint = Skeleton(frame).joints[central]
            last_joint:Skeleton.Joint = Skeleton(frame).joints[last]

            first_vector = Calculate.Vector(central_joint, first_joint)
            second_vector = Calculate.Vector(central_joint, last_joint)
        
        except KeyError:
            return np.nan
        else:
            return first_vector // second_vector
    
    def read_json(self):
        with open(self.file3d) as f:
            data: list = json.load(f)['localizations']
        return data

if __name__ == "__main__":
    calc = Calculate('videos/p001g01_3d.json')
    calc.run_frames()
