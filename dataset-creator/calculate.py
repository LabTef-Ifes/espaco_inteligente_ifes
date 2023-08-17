# -*- coding: utf-8 -*-
from collections import defaultdict
import os
import json
import numpy as np
import math
from collections import defaultdict
import matplotlib.pyplot as plt

"""
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
"""


class Skeleton:
    """Classe que representa um esqueleto. Guarda os pontos do esqueleto em um dicionário, onde a chave é o id do ponto e o valor é um objeto da classe Joint.
    Classe usada exclusivamente para o cálculo de posições, ângulos e distâncias entre os pontos do esqueleto.
    """

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
            self.name = Calculate.human_parts_id.get(id, "Placeholder")
            self.x = x
            self.y = y
            self.z = z

        def __str__(self):
            return f"Joint: {self.name} | x: {self.x:.4f} | y: {self.y:.4f} | z: {self.z:.4f}"

        __repr__ = __str__

        def __add__(self, other):
            """Soma dois pontos do esqueleto, retornando um novo ponto com as coordenadas somadas

            Args:
                other (Joint): outro ponto do esqueleto

            Returns:
                Joint: novo ponto com as coordenadas somadas
            """
            return Skeleton.Joint(
                "sum", self.x + other.x, self.y + other.y, self.z + other.z
            )

    def __init__(self, frame_dict: dict):
        """Recebe um dicionario que possui as chaves "objects" e "keypoints" e salva um objeto com os dados do esqueleto no frame.

        Args:
            frame_dict (dict): dicionario que contém "objects" com seus keypoints
        """
        self.objects: list[dict] = frame_dict[
            "objects"
        ]  # Lista de objetos(pessoas) no frame
        # Lista os keypoints de todos os esqueletos presentes
        self.keypoints: list[dict] = [human["keypoints"] for human in self.objects]
        self.joints: dict[str, Skeleton.Joint] = self.read_joints()

    def read_joints(self):
        """Lê os pontos do esqueleto e os salva em um dicionário

        Returns:
            dict[str,Skeleton.Joint]: Dicionário com os pontos do esqueleto
        """
        joints: dict[str, Skeleton.Joint] = {}
        for human in self.objects:
            for keypoint in human["keypoints"]:
                position = keypoint["position"]
                joints[keypoint["id"]] = Skeleton.Joint(
                    keypoint["id"], position["x"], position["y"], position["z"]
                )
        return joints


class Calculate:
    human_parts_id: dict = {
        "0": "UNKNOWN_HUMAN_KEYPOINT",
        "1": "HEAD",
        "2": "NOSE",
        "3": "NECK",
        "4": "RIGHT_SHOULDER",
        "5": "RIGHT_ELBOW",
        "6": "RIGHT_WRIST",
        "7": "LEFT_SHOULDER",
        "8": "LEFT_ELBOW",
        "9": "LEFT_WRIST",
        "10": "RIGHT_HIP",
        "11": "RIGHT_KNEE",
        "12": "RIGHT_ANKLE",
        "13": "LEFT_HIP",
        "14": "LEFT_KNEE",
        "15": "LEFT_ANKLE",
        "16": "RIGHT_EYE",
        "17": "LEFT_EYE",
        "18": "RIGHT_EAR",
        "19": "LEFT_EAR",
        "20": "CHEST",
    }
    human_parts_name = {
        "UNKNOWN_HUMAN_KEYPOINT": "0",
        "HEAD": "1",
        "NOSE": "2",
        "NECK": "3",
        "RIGHT_SHOULDER": "4",
        "RIGHT_ELBOW": "5",
        "RIGHT_WRIST": "6",
        "LEFT_SHOULDER": "7",
        "LEFT_ELBOW": "8",
        "LEFT_WRIST": "9",
        "RIGHT_HIP": "10",
        "RIGHT_KNEE": "11",
        "RIGHT_ANKLE": "12",
        "LEFT_HIP": "13",
        "LEFT_KNEE": "14",
        "LEFT_ANKLE": "15",
        "RIGHT_EYE": "16",
        "LEFT_EYE": "17",
        "RIGHT_EAR": "18",
        "LEFT_EAR": "19",
        "CHEST": "20",
    }

    class Vector:
        """Um segmento do corpo pode ser tratado como um vetor, com origem no ponto A e destino no ponto B. Assim, usamos álgebra para obter sua magnitude e ângulo criando vetores entre dois pontos do corpo."""

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
        def magnitude(self) -> float:
            return np.linalg.norm(self.vector)

        def calculate_angle(self, vector):
            """Calcula o ângulo entre dois vetores usando produto interno

            Args:
                vector (Vector): Outro vetor com o mesmo ponto de origem

            Returns:
                float: angulo em graus
            """
            assert (
                self.point_a == vector.point_a
            ), "Os vetores devem ter o mesmo ponto de origem"
            return math.degrees(
                math.acos(
                    np.dot(self.vector, vector.vector)
                    / (self.magnitude * vector.magnitude)
                )
            )

        # Define a operação //
        def __floordiv__(self, other):
            return self.calculate_angle(other)

    def tratar_erro_frame(func):
        """Decorator para fazer o try except automaticamente em todas as funções de cálculo.

        Args:
            func (function): Função que será decorada(Usa-se o @tratar_erro_frame acima da função)
        """        
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except Exception as e:
                print(f"Erro {e}")
                return np.nan

            return result

        return wrapper

    def __init__(self, file3d):
        # Dicionario para guardar as informações que serão plotadas posteriormente
        self.plot_data: defaultdict = defaultdict(list)
        self.file3d = file3d
        self.data = self.read_json()
        self.frames = len(self.data)
        self.skeleton: Skeleton = Skeleton(self.data[0])
        self.dt = 1 / 6  # Tempo entre cada frame. inverso de frames por segundo

    def run_frames(self):
        """Passa por todos os frames, calculando as informações necessárias para o plot usando a classe Skeleton para guardar as informações. Ao final, chama a função que plota os dados"""
        for i, frame_info in enumerate(self.data):
            self.skeleton = Skeleton(frame_info) #Atualiza o esqueleto do frame
            # Distancia

            ## Distancia dos pés
            self.plot_data["distancia_pes"].append(self.distancia_pes())

            # Altura

            ## Altura do pé
            self.plot_data["altura_pe_esquerdo"].append(self.altura_do_pe("esquerdo"))
            self.plot_data["altura_pe_direito"].append(self.altura_do_pe("direito"))

            # Calcula os ângulos entre os segmentos do corpo

            ## Angulo do tronco com o eixo vertical
            self.plot_data["angulo_tronco"].append(self.angulo_tronco_vertical())

            ## Joelho esquerdo
            self.plot_data["angulo_joelho_esquerdo"].append(
                self.angulo_joelho_esquerdo()
            )
            ## Joelho direito
            self.plot_data["angulo_joelho_direito"].append(self.angulo_joelho_direito())

    @tratar_erro_frame
    def angulo_tronco_vertical(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        joint_tronco = self.human_parts_name["CHEST"]
        joint_neck = self.human_parts_name["NECK"]
        chest: Skeleton.Joint = self.skeleton.joints[joint_tronco]
        neck: Skeleton.Joint = self.skeleton.joints[joint_neck]
        point_vertical = chest + Skeleton.Joint(
            "vertical", 0, 0, 1
        )  # uma unidade de z acima do chest

        vertical_vector = Calculate.Vector(
            chest, point_vertical
        )  # Vetor paralelo ao eixo z
        chest_neck_vector = Calculate.Vector(
            chest, neck
        )  # Vetor entre o peito e o pescoço

        return round(vertical_vector // chest_neck_vector, 3)  # Angulo

    @tratar_erro_frame
    def distancia_pes(self):
        pe_esquerdo = self.human_parts_name["LEFT_ANKLE"]
        pe_direito = self.human_parts_name["RIGHT_ANKLE"]
        joint_pe_esquerdo = self.skeleton.joints[pe_esquerdo]
        joint_pe_direito = self.skeleton.joints[pe_direito]
        vetor = Calculate.Vector(joint_pe_esquerdo, joint_pe_direito)

        return vetor.magnitude

    @tratar_erro_frame
    def _calculate_angle(self, first, central, last):
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
        first_joint = self.skeleton.joints[first]
        central_joint = self.skeleton.joints[central]
        last_joint = self.skeleton.joints[last]
        first_vector = Calculate.Vector(central_joint, first_joint)
        second_vector = Calculate.Vector(central_joint, last_joint)
        return round(first_vector // second_vector, 3)

    def angulo_joelho_direito(self):
        return self._calculate_angle("10", "11", "12")

    def angulo_joelho_esquerdo(self):
        return self._calculate_angle("13", "14", "15")

    @tratar_erro_frame
    def altura_do_pe(self, lado: str):
        assert lado in ("esquerdo", "direito"), 'Lado deve ser "esquerdo" ou "direito"'
        joint_pe = (
            self.human_parts_name["RIGHT_ANKLE"]
            if lado == "direito"
            else self.human_parts_name["LEFT_ANKLE"]
        )
        pe = self.skeleton.joints[joint_pe]

        chao = Skeleton.Joint("chao", 0, 0, 0)

        altura = Calculate.Vector(chao, pe)
        return abs(altura.z)

    def read_json(self):
        with open(self.file3d) as f:
            data: list = json.load(f)["localizations"]
        return data


class Plot:
    PASTA_RESULTADO = "resultados"

    def __init__(self, data):
        os.makedirs(self.PASTA_RESULTADO, exist_ok=True)
        self.data = data

        self.plot()

    def plot(self):
        self.plot_joelho()
        self.plot_tronco()
        self.plot_altura_pe()
        self.plot_distancia_pes()

    def plot_distancia_pes(self):
        fig, ax = plt.subplots()
        ax.plot(self.data["distancia_pes"], label="Distância entre os pés")
        ax.set_title("Distância entre os pés(m)")
        ax.set_xlabel("Frame")
        ax.set_ylabel("Distância(m)")
        ax.legend()
        plt.savefig(os.path.join(self.PASTA_RESULTADO, "distancia_pes.png"))

    def plot_joelho(self):
        fig, ax = plt.subplots()
        ax.plot(self.data["angulo_joelho_direito"], label="Joelho Direito")
        ax.plot(self.data["angulo_joelho_esquerdo"], label="Joelho Esquerdo")
        ax.set_title("Ângulo do Joelho(graus)")
        ax.set_xlabel("Frame")
        ax.set_ylabel("Ângulo")
        ax.legend()

        plt.savefig(os.path.join(self.PASTA_RESULTADO, "angulo_joelho.png"))

    def plot_tronco(self):
        fig, ax = plt.subplots()
        ax.plot(self.data["angulo_tronco"], label="Ângulo do tronco")
        ax.set_title("Ângulo do tronco(graus)")
        ax.set_xlabel("Frame")
        ax.set_ylabel("Ângulo com o plano vertical")
        ax.legend()
        plt.savefig(os.path.join(self.PASTA_RESULTADO, "angulo_tronco.png"))

    def plot_altura_pe(self):
        fig, ax = plt.subplots()
        ax.plot(self.data["altura_pe_esquerdo"], label="Pé Esquerdo")
        ax.plot(self.data["altura_pe_direito"], label="Pé Direito")
        ax.set_title("Altura do Pé(metros)")
        ax.set_xlabel("Frame")
        ax.set_ylabel("Altura")
        ax.legend()

        plt.savefig(os.path.join(self.PASTA_RESULTADO, "altura_pe.png"))


if __name__ == "__main__":
    calc = Calculate("videos/p001g01_3d.json")
    calc.run_frames()
    print(calc.plot_data["altura_pe_direito"])

    plot = Plot(calc.plot_data)
