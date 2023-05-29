import csv
import io
import json
import math
import statistics
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
import tensorflow as tf
from google.protobuf.json_format import ParseDict
from is_msgs.image_pb2 import ObjectAnnotations
from skfuzzy import control as ctrl
from sklearn import preprocessing
from utils import load_options

with open('keymap.json') as f:
    keymap = json.load(f)

options = load_options(print_options=False)


# classe sem self???
class Parameter:
    @staticmethod
    def perdas_3d(ax, skeletons, links, colors):
        """

        Args:
            ax: não usado???
            skeletons:
            links:
            colors:

        Returns:

        """
        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
        for skeleton in skeletons_pb.objects:
            parts = {}
            for part in skeleton.keypoints:
                parts[part.id] = (
                    part.position.x, part.position.y, part.position.z)
            for link_parts, color in zip(links, colors):
                begin, end = link_parts
                if begin in parts and end in parts:

                    perdas = (15 - len(parts)) / 15.0
                    perdas = perdas * 100.0
                    return perdas

    # perna direita e angulo_real_joelho_esquerdo não usados
    @staticmethod
    def erro_medio_da_caminhada(comprimento_passo_real_medido, Stance_real, Swing_real, distance_feet,
                                dist_dos_pes_inicial, picos_distancia, comprimento_passo_medido, comprimento_swing,
                                comprimento_stance, angulo_caminhada, altura_quadril, perna_direita, left_knee_angle,
                                angulo_real_joelho_esquerdo, flexion_left_knee, flexion_right_knee,
                                simetria_comprimento_passo, largura_da_passada, left_extension_hip_angle,
                                right_extension_hip_angle):
        """_summary_

        Args:
            comprimento_passo_real_medido (_type_): _description_
            Stance_real (_type_): _description_
            Swing_real (_type_): _description_
            distance_feet (_type_): _description_
            dist_dos_pes_inicial (_type_): _description_
            picos_distancia (_type_): _description_
            comprimento_passo_medido (_type_): _description_
            comprimento_swing (_type_): _description_
            comprimento_stance (_type_): _description_
            angulo_caminhada (_type_): _description_
            altura_quadril (_type_): _description_
            perna_direita (_type_): _description_
            left_knee_angle (_type_): _description_
            angulo_real_joelho_esquerdo (_type_): _description_
            flexion_left_knee (_type_): _description_
            flexion_right_knee (_type_): _description_
            simetria_comprimento_passo (_type_): _description_
            largura_da_passada (_type_): _description_
            left_extension_hip_angle (_type_): _description_
            right_extension_hip_angle (_type_): _description_
        """

        # Poderia ser um Defaultdict(list)
        vetor_erro_comprimento_de_passo = []
        vetor_erro_comprimento_de_meio_passo = []
        vetor_erro_comprimento_swing = []
        vetor_erro_comprimento_stance = []
        vetor_erro_distancia_dos_pes_inicial = []
        dist = [dist_dos_pes_inicial, distance_feet[0]]

        comprimento_medio_real_de_meio_passo = (Stance_real + Swing_real) / 2
        erro_medio_comprimento_de_passo = comprimento_passo_real_medido - \
            statistics.mean(comprimento_passo_medido)

        # Poderia ser generator
        for j in range(len(comprimento_passo_medido)):
            vetor_erro_comprimento_de_passo.append(
                abs(comprimento_passo_real_medido - comprimento_passo_medido[j]))

        for j in range(len(picos_distancia)):
            vetor_erro_comprimento_de_meio_passo.append(
                abs(comprimento_medio_real_de_meio_passo - picos_distancia[j]))

        for j in range(len(comprimento_stance)):
            vetor_erro_comprimento_stance.append(
                abs(Stance_real - comprimento_stance[j]))

        for j in range(len(comprimento_swing)):
            vetor_erro_comprimento_swing.append(
                abs(Swing_real - comprimento_swing[j]))

        for j in range(len(dist)):
            vetor_erro_distancia_dos_pes_inicial.append(
                abs(dist_dos_pes_inicial - dist[j]))

        erro_medio_meio_comprimento_de_passo = (
            comprimento_medio_real_de_meio_passo - statistics.mean(picos_distancia))
        print("Comprimento médio de passada: %.4f m " %
              statistics.mean(comprimento_passo_medido))
        print("Erro absoluto médio do comprimento da passada: %.3f m" %
              abs(erro_medio_comprimento_de_passo))
        print("Desvio padrão comprimento da passada medida: %.3f m" %
              abs(statistics.pstdev(comprimento_passo_medido)))
        print("Desvio padrão do erro do comprimento da passada em %.3f m" %
              abs(statistics.pstdev(vetor_erro_comprimento_de_passo)))
        print("Comprimento médio de meio passo: %.4f m " %
              statistics.mean(picos_distancia))
        print("Erro absoluto médio do meio comprimento de passo: %.3f m" %
              abs(erro_medio_meio_comprimento_de_passo))
        print("Desvio padrão do comprimento médio de meio passo: %.3f m" %
              abs(statistics.pstdev(picos_distancia)))

        erro_swing = Swing_real - statistics.mean(comprimento_swing)
        print("Desvio padrão do erro de comprimento de meio passo em %.3f m" %
              abs(statistics.pstdev(vetor_erro_comprimento_de_meio_passo)))
        print("Largura de passo: %.3f " % statistics.mean(largura_da_passada))
        print("Erro da largura de passo: %.3f " %
              (dist_dos_pes_inicial - statistics.mean(largura_da_passada)))
        print("Desvio padrão da largura de passo: %.3f" %
              statistics.pstdev(largura_da_passada))
        print("Comprimento do Swing: %.4f m " %
              statistics.mean(comprimento_swing))
        print("Erro absoluto médio do swing: %.3f m" % abs(erro_swing))
        print("Desvio padrão do swing: %.3f m" %
              abs(statistics.pstdev(comprimento_swing)))
        print("Desvio padrão do erro de swing em %.4f m " %
              abs(statistics.pstdev(vetor_erro_comprimento_swing)))

        erro_stance = Stance_real - statistics.mean(comprimento_stance)
        print("Comprimento do Stance: %.4f m " %
              statistics.mean(comprimento_stance))
        print("Erro absoluto médio do stance: %.3f m" % abs(erro_stance))
        print("Desvio padrão do stance: %.3f m" %
              abs(statistics.pstdev(comprimento_stance)))
        print("Desvio padrão do erro de stance em %.4f m" %
              abs(statistics.pstdev(vetor_erro_comprimento_stance)))

        erro_dist_inicial = dist_dos_pes_inicial - distance_feet[0]
        print("Distância inicial do pé: %.3f m " % distance_feet[0])
        print("Erro absoluto médio da distância entre os pés: %.3f m " %
              abs(erro_dist_inicial))
        print("Desvio padrão da distância inicial entre os pés: %.3f m " %
              abs(statistics.pstdev(dist)))
        print("Desvio padrão do erro da distância inicial entre os pés em %.4f m" % abs(
            statistics.pstdev(vetor_erro_distancia_dos_pes_inicial)))

        # aux2 = aux/(2*b*c)
        # erro_medio_angulo=math.degrees(math.acos(aux2))-statistics.mean(angulo_caminhada)
        # print("Ângulo real de abertura das pernas: %.3f °" % math.degrees(math.acos(aux2)))
        # print(math.degrees(math.acos(aux2)))
        # print(math.degrees(math.acos(((2*((altura_quadril)**2)-Stance_real)/(2*((statistics.mean(perna_direita))**2))))))
        print("Ângulo médio de abertura das pernas durante a caminhada: %.3f" %
              statistics.mean(angulo_caminhada) + "°")
        # print("Erro absoluto médio, em graus, do angulo entre as pernas: %.3f" % abs(erro_medio_angulo) + "°")
        print("Desvio padrão do ângulo médio de abertura das pernas durante a caminhada: %.3f" % abs(
            statistics.pstdev(angulo_caminhada)) + "°")
        print("Número de amostras do ângulo de abertura das pernas durante a caminhada: %i" % len(
            angulo_caminhada))
        print("Ângulo médio da coxa do joelho da perna esquerda: %.3f graus" %
              statistics.mean(left_knee_angle))
        # print("Erro do angulo do joelho esquerdo: %.3f graus" % (angulo_real_joelho_esquerdo-(statistics.mean(
        # left_knee_angle))))
        print("Desvio padrao do angulo médio de abertura do joelho da perna esquerda: %.3f graus" %
              statistics.pstdev(left_knee_angle))
        print("Ângulo de flexão do joelho esquerdo: %.3f ° " %
              statistics.mean(flexion_left_knee))
        print("Desvio padrão do ângulo de flexão do joelho esquerdo: %.3f °" %
              statistics.pstdev(flexion_left_knee))
        print("Ângulo de flexão do joelho direito: %.3f ° " %
              statistics.mean(flexion_right_knee))
        print("Desvio padrão do ângulo de flexão do joelho direito: %.3f °" %
              statistics.pstdev(flexion_right_knee))
        print("Ângulo extensão do quadril esquerdo: %.3f °" %
              statistics.mean(left_extension_hip_angle))
        print("Desvio padrão do ângulo de extensão do quadril esquerdo: %.3f º" %
              statistics.pstdev(left_extension_hip_angle))
        print("Ângulo extensão do quadril direito: %.3f °" %
              statistics.mean(right_extension_hip_angle))
        print("Desvio padrão do ângulo de extensão do quadril direito: %.3f º" %
              statistics.pstdev(right_extension_hip_angle))
        print("Simetria da comprimento de passo: %.3f " %
              statistics.mean(simetria_comprimento_passo))
        print("Desvio padrão da simetria do comprimento de passo: %.3f " %
              statistics.pstdev(simetria_comprimento_passo))

    @staticmethod
    def left_leg(skeletons):
        left_ankle = 0
        left_hip = 0
        left_knee = 0
        quadril_ang = 0
        # Não usados???
        '''left_leg = 0
        aux_left_leg = 0
        left_knee_angle = 0
        razao = 0
        angle_test = 0
        delta_y = 0
        delta_z = 0'''
        neck = []
        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())

        if skeletons_pb.objects:
            # overwrites skeletons???
            for skeletons in skeletons_pb.objects:
                parts = {}
                for part in skeletons.keypoints:
                    parts[part.id] = (
                        part.position.x, part.position.y, part.position.z)
                    if part.id == 3:
                        neck = parts[3]
                    elif part.id == 13:
                        left_hip = parts[13]
                    elif part.id == 14:
                        left_knee = parts[14]
                    elif part.id == 15:
                        left_ankle = parts[15]

                if left_ankle and left_hip and left_knee and neck:
                    left_hip = parts[13]
                    left_knee = parts[14]
                    left_ankle = parts[15]
                    a = np.sqrt((left_ankle[0] - left_knee[0]) ** 2 + (
                        left_ankle[1] - left_knee[1]) ** 2 + (left_ankle[2] - left_knee[2]) ** 2)
                    b = np.sqrt((left_knee[0] - left_hip[0]) ** 2 + (left_knee[1] -
                                                                     left_hip[1]) ** 2 + (
                        left_knee[2] - left_hip[2]) ** 2)
                    left_leg = a + b
                    aux_left_leg = left_leg

                    c = np.sqrt((left_hip[1] - left_ankle[1])
                                ** 2 + (left_hip[2] - left_ankle[2]) ** 2)
                    a = np.sqrt((left_hip[1] - left_knee[1])
                                ** 2 + (left_hip[2] - left_knee[2]) ** 2)
                    b = np.sqrt((left_knee[1] - left_ankle[1])
                                ** 2 + (left_knee[2] - left_ankle[2]) ** 2)
                    produto = ((pow(a, 2) + pow(b, 2) -
                               pow(c, 2)) / (2 * a * b))
                    left_knee_angle = (180 - math.degrees(math.acos(produto)))

                    v0 = ((neck[1] - left_hip[1]), (neck[2] - left_hip[2]))
                    v1 = ((left_knee[1] - left_hip[1]),
                          (left_knee[2] - left_hip[2]))
                    ang = math.degrees(np.math.atan2(
                        np.linalg.det([v0, v1]), np.dot(v0, v1)))


                    delta_y = left_knee[1] - left_hip[1]
                    delta_z = left_knee[2] - left_hip[2]
                    razao = delta_y / delta_z
                    # CALCULADO COM A LUÍZA DIA 08/01/2021 - extansão do quadril esquerdo
                    angle_test = -1 * math.degrees(np.math.atan(razao))
                    quadril_ang = angle_test

                    # Return estranhos, parecem encerrar o código em 1 loop
                    return left_leg, aux_left_leg, left_knee_angle, quadril_ang
                else:
                    left_leg = 0
                    left_knee_angle = 0
                    aux_left_leg = 0

                    return left_leg, aux_left_leg, left_knee_angle, quadril_ang
        else:
            left_leg = 0
            left_knee_angle = 0
            aux_left_leg = 0
            return left_leg, aux_left_leg, left_knee_angle, quadril_ang

    @staticmethod
    def ang_plano_torax(skeletons):
        neck = 0
        left_hip = left_knee = right_hip = right_knee = 0
        vetor_normal = [0, 0, 0]
        angle_test = 0
        ponto_peito = [0, 0, 0]
        # Não usados???
        '''v1 = v2 = 0
        angle = ang = angle_right = angle_left = 0'''

        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())

        for skeletons in skeletons_pb.objects:
            parts = {}
            for part in skeletons.keypoints:
                parts[part.id] = (
                    part.position.x, part.position.y, part.position.z)
                if part.id == 3:
                    neck = parts[3]
                elif part.id == 10:
                    right_hip = parts[10]
                elif part.id == 11:
                    right_knee = parts[11]
                elif part.id == 13:
                    left_hip = parts[13]
                elif part.id == 14:
                    left_knee = parts[14]
                elif part.id == 20:
                    ponto_peito = parts[20]

                if left_hip and right_hip and neck and right_knee and left_knee:
                    v1_x, v1_y, v1_z = (
                        right_hip[0] - left_hip[0]), (right_hip[1] - left_hip[1]), (
                        right_hip[2] - left_hip[2])

                    v1 = np.array([v1_x, v1_y, v1_z])
                    v2_x, v2_y, v2_z = (
                        right_hip[0] - neck[0]), (right_hip[1] - neck[1]), (
                        right_hip[2] - neck[2])
                    v2 = np.array([v2_x, v2_y, v2_z])
                    vetor_normal = np.cross(v1, v2)

                    v3 = ((right_hip[0] + left_hip[0]), (right_hip[1] +
                                                         left_hip[1]), (right_hip[2] + left_hip[2]) / 2)
                    # (neck[0]-v3[0],neck[1]-v3[1],neck[2]-v3[2])
                    v3_1 = (0, 0, 1)
                    vetor_normal = vetor_normal / np.linalg.norm(vetor_normal)
                    v3_1 = v3_1 / np.linalg.norm(v3_1)
                    # Flexão do tórax durante a caminhada
                    # angle = 90 - math.degrees(np.arccos(dot_product))
                    v0 = ((neck[1] - right_hip[1]), (neck[2] - right_hip[2]))
                    v1 = ((right_knee[1] - right_hip[1]),
                          (right_knee[2] - right_hip[2]))
                    ang = math.degrees(np.math.atan2(
                        np.linalg.det([v0, v1]), np.dot(v0, v1)))
                    delta_y = right_knee[1] - right_hip[1]
                    delta_z = right_knee[2] - right_hip[2]
                    razao = delta_y / delta_z
                    # CALCULADO COM A LUÍZA DIA 08/01/2021 - extensão do quadril direito
                    angle_test = -1 * math.degrees(np.math.atan(razao))

                    '''if ang < 0:
                        angle_right = -(180 + ang)
                        # print("aqui")
                    else:
                        angle_right = 180 - ang'''
                    # np.dot(vetor_lateral_right_costas,vetor_lateral_right_coxa)))
                    # angle_left=degrees(np.arccos(dot_product))
                    # print(angle_right)
                else:
                    vetor_normal = [0, 0, 0]

        return angle_test, vetor_normal, ponto_peito

    @staticmethod
    def flexion_left_knee(skeletons):
        """_summary_

        Args:
            skeletons (_type_): _description_

        Returns:
            _type_: _description_
        """

        left_hip = left_knee = left_leg = 0
        ang_flex_left_knee = 0

        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
        for skeletons in skeletons_pb.objects:
            parts = {}
            for part in skeletons.keypoints:
                parts[part.id] = (
                    part.position.x, part.position.y, part.position.z)
                if part.id == 13:
                    left_hip = parts[13]
                elif part.id == 14:
                    left_knee = parts[14]
                if left_hip and left_knee:
                    a = left_hip[1] - left_knee[1]
                    b = left_hip[0] - left_knee[0]
                    c = (a / b)
                    ang_flex_left_knee = math.degrees(math.atan(c))
                    # print(a,b,ang_flex_left_knee)
        return ang_flex_left_knee

    @staticmethod
    def right_leg(skeletons):
        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
        right_hip = None
        right_knee = None
        right_ankle = None
        left_ankle = None
        altura_pe_esquerdo = altura_pe_direito = 0
        # Não usados???
        '''right_leg = None
        height_mid_point_ankle = None
        largura_de_passo = None'''

        if skeletons_pb.objects:
            for skeletons in skeletons_pb.objects:
                parts = {}
                for part in skeletons.keypoints:
                    parts[part.id] = (
                        part.position.x, part.position.y, part.position.z)
                    if part.id == 10:
                        right_hip = parts[10]
                    elif part.id == 11:
                        right_knee = parts[11]
                    elif part.id == 12:
                        right_ankle = parts[12]
                    elif part.id == 15:
                        left_ankle = parts[15]

                if right_ankle and right_knee and right_hip and left_ankle:
                    a = np.sqrt((right_ankle[0] - right_knee[0]) ** 2 + (
                        right_ankle[1] - right_knee[1]) ** 2 + (right_ankle[2] - right_knee[2]) ** 2)
                    b = np.sqrt((right_knee[0] - right_hip[0]) ** 2 + (
                        right_knee[1] - right_hip[1]) ** 2 + (right_knee[2] - right_hip[2]) ** 2)
                    right_leg = a + b
                    altura_pe_esquerdo = left_ankle[2]
                    altura_pe_direito = right_ankle[2]
                    height_mid_point_ankle = (
                        left_ankle[2] + right_ankle[2]) / 2
                    # Largura de passo - distância entre os pés
                    largura_de_passo = np.sqrt(
                        (right_ankle[0] - left_ankle[0]) ** 2)

                    right_leg_angle_e_quadril_ang = math.degrees(
                        math.atan(abs((right_ankle[1] - right_knee[1]) / (right_knee[2] - right_ankle[2]))))
                    # quadril_ang = math.degrees(
                    #    abs(math.atan(abs((right_knee[1] - right_hip[1]) / (right_hip[2] - right_knee[2])))))

                    C = np.sqrt((right_hip[1] - right_ankle[1])
                                ** 2 + (right_hip[2] - right_ankle[2]) ** 2)
                    A = np.sqrt((right_hip[1] - right_knee[1])
                                ** 2 + (right_hip[2] - right_knee[2]) ** 2)
                    B = np.sqrt((right_knee[1] - right_ankle[1])
                                ** 2 + (right_knee[2] - right_ankle[2]) ** 2)
                    produto = ((pow(A, 2) + pow(B, 2) -
                               pow(C, 2)) / (2 * A * B))
                    ang_produto = math.degrees(math.acos(produto))

                    if right_leg_angle_e_quadril_ang:
                        right_knee_angle = (180 - ang_produto)
                        # right_knee_angle=right_leg_angle_e_quadril_ang-quadril_ang
                        # print(right_knee_angle)
                    else:
                        right_knee_angle = 0
                        # right_knee_angle=-right_leg_angle_e_quadril_ang+quadril_ang
                        # print(right_knee_angle)

                    # c=np.sqrt((right_hip[0]-right_ankle[0])**2+(right_hip[1]-right_ankle[1])**2+(right_hip[2]-right_ankle[2])**2)
                    # B=pow(c,2)-(pow(a,2)+pow(b,2))
                    # A=-2*b*c
                    # print(a,b,c,B,A)
                    # print(left_leg,aux_left_leg,left_knee_angle)
                    # if (A!=0):
                    # if ((B/A)<1):
                    # right_knee_angle=(180-math.degrees(math.acos(B/A)))
                    # print(left_leg,aux_left_leg,left_knee_angle)
                    # else:
                    # right_knee_angle=0

                    return right_leg, height_mid_point_ankle, largura_de_passo, right_knee_angle, altura_pe_direito, altura_pe_esquerdo, right_ankle, left_ankle

                else:
                    height_mid_point_ankle = 0
                    right_leg = 0
                    largura_de_passo = 0
                    right_knee_angle = 0
                    return right_leg, height_mid_point_ankle, largura_de_passo, right_knee_angle, altura_pe_direito, altura_pe_esquerdo, right_ankle, left_ankle

        else:
            height_mid_point_ankle = 0
            right_leg = 0
            largura_de_passo = 0
            right_knee_angle = 0
            return right_leg, height_mid_point_ankle, largura_de_passo, right_knee_angle, altura_pe_direito, altura_pe_esquerdo, right_ankle, left_ankle

    @staticmethod
    def velocidade_angular(angulo, intervalo_de_tempo):
        velocidade_angular = angulo / intervalo_de_tempo
        return velocidade_angular

    @staticmethod
    def fuzzy(velocidade_media, cadencia_medido, largura_media, comprimento_passo_medido, comprimento_passo_real_medido,
              dist_dos_pes_inicial):
        """_summary_

        Args:
            velocidade_media (_type_): _description_
            cadencia_medido (_type_): _description_
            largura_media (_type_): _description_
            comprimento_passo_medido (_type_): _description_
            comprimento_passo_real_medido (_type_): _description_
            dist_dos_pes_inicial (_type_): _description_

        Returns:
            _type_: _description_
        """

        cadencia = ctrl.Antecedent(np.arange(0, 210, 1), 'cadencia')
        velocidade = ctrl.Antecedent(np.arange(0, 4, 1), 'velocidade')
        largura = ctrl.Antecedent(np.arange(0, 4, 1), 'largura')
        comprimento = ctrl.Antecedent(np.arange(0, 4, 1), 'comprimento')

        # Resultado dos valores de entrada
        resultado = ctrl.Consequent(np.arange(0, 10, 1), 'Movimento')

        velocidade['lenta'] = fuzz.trimf(velocidade.universe, [0, 0, 1])
        # fuzz.gaussmf(cadencia.universe, 5, 2)
        velocidade['normal'] = fuzz.trimf(velocidade.universe, [0, 1, 2])
        velocidade['rápido'] = fuzz.trapmf(velocidade.universe, [2, 2, 3, 3])

        # Cria as funções de pertinência usando tipos variados
        cadencia['baixa'] = fuzz.trimf(cadencia.universe, [0, 0, 110])
        # fuzz.gaussmf(cadencia.universe, 5, 2)
        cadencia['normal'] = fuzz.trimf(cadencia.universe, [0, 110, 220])
        # fuzz.gaussmf(cadencia.universe, 100,30)
        cadencia['alta'] = fuzz.trimf(cadencia.universe, [110, 220, 330])

        largura['pequena'] = fuzz.trimf(largura.universe, [0, 0, 1])
        largura['normal'] = fuzz.trimf(largura.universe, [0, 1, 2])
        largura['grande'] = fuzz.trimf(largura.universe, [1, 2, 3])

        comprimento['pequeno'] = fuzz.trimf(comprimento.universe, [0, 0, 1])
        comprimento['normal'] = fuzz.trimf(comprimento.universe, [0, 1, 2])
        comprimento['grande'] = fuzz.trimf(comprimento.universe, [1, 2, 3])

        resultado['errado'] = fuzz.trimf(resultado.universe, [0, 0, 5])
        # resultado['indefinido'] = fuzz.trimf(resultado.universe, [0, 5, 9])
        resultado['certo'] = fuzz.trimf(resultado.universe, [5, 9, 9])

        velocidade.view()
        plt.savefig(options.folder + '/velocidade.png')
        largura.view()
        plt.savefig(options.folder + '/largura.png')
        cadencia.view()
        plt.savefig(options.folder + '/cadencia.png')
        comprimento.view()
        plt.savefig(options.folder + '/comprimento.png')
        resultado.view()
        plt.savefig(options.folder + '/resultado.png')

        # Regras para a classificação

        rule1 = ctrl.Rule(velocidade['normal'] & cadencia['normal'] &
                          largura['normal'] & comprimento['normal'], resultado['certo'])
        rule2 = ctrl.Rule(velocidade['rápido'] & cadencia['alta'] &
                          largura['normal'] & comprimento['normal'], resultado['certo'])
        rule3 = ctrl.Rule(velocidade['rápido'] & cadencia['normal'] &
                          largura['normal'] & comprimento['grande'], resultado['errado'])
        rule4 = ctrl.Rule(velocidade['lenta'] &
                          cadencia['baixa'], resultado['errado'])
        rule5 = ctrl.Rule(velocidade['normal'] & largura['normal']
                          & comprimento['normal'], resultado['certo'])
        rule6 = ctrl.Rule(largura['pequena'] |
                          comprimento['pequeno'], resultado['errado'])
        rule7 = ctrl.Rule(largura['grande'] |
                          comprimento['grande'], resultado['errado'])
        rule8 = ctrl.Rule(velocidade['normal'] & cadencia['baixa'] &
                          largura['normal'] & comprimento['normal'], resultado['certo'])
        rule9 = ctrl.Rule(velocidade['lenta'] & cadencia['baixa'] &
                          largura['pequena'] & comprimento['pequeno'], resultado['errado'])
        rule10 = ctrl.Rule(velocidade['normal'] & cadencia['baixa'] &
                           largura['normal'] & comprimento['normal'], resultado['errado'])
        rule11 = ctrl.Rule(velocidade['rápido'] & cadencia['normal'] &
                           largura['normal'] & comprimento['normal'], resultado['certo'])
        rule12 = ctrl.Rule(velocidade['normal'] & cadencia['baixa'] &
                           largura['grande'] & comprimento['normal'], resultado['errado'])
        rule13 = ctrl.Rule(cadencia['normal'] & largura['normal']
                           & comprimento['normal'], resultado['certo'])
        rule14 = ctrl.Rule(velocidade['rápido'] &
                           cadencia['baixa'], resultado['errado'])
        rule15 = ctrl.Rule(cadencia['baixa'], resultado['errado'])

        movimento_ctrl = ctrl.ControlSystem(
            [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule9, rule10, rule11, rule12, rule13, rule14, rule15])
        movimento_simulador = ctrl.ControlSystemSimulation(movimento_ctrl)

        # Entrando com alguns valores para qualidade da comida e do serviço
        movimento_simulador.input['velocidade'] = (velocidade_media / 1.37)
        movimento_simulador.input['cadencia'] = cadencia_medido
        movimento_simulador.input['largura'] = (
            largura_media / dist_dos_pes_inicial)
        movimento_simulador.input['comprimento'] = (statistics.mean(
            comprimento_passo_medido) / comprimento_passo_real_medido)

        # Computando o resultado
        movimento_simulador.compute()
        resultado = movimento_simulador.output['Movimento']
        # print(resultado)

        velocidade.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/velocidade_simulator.png')
        cadencia.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/cadencia_simulator.png')
        largura.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/largura_simulator.png')
        comprimento.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/comprimento_simulator.png')
        # resultado.view(sim=movimento_simulador)
        # plt.savefig(options.folder+'/resultado_simulator.png')
        # time.time()
        return resultado

    @staticmethod
    def fuzzy_6_movimentos(velocidade_media, cadencia_medido, largura_media, comprimento_medio_passada,
                           comprimento_passo_medido, flexion_left_knee_angle, flexion_right_knee_angle,
                           simetria_comprimento_passo, ang_ext_quadril, aux_angulo):

        velocidade = ctrl.Antecedent(np.arange(0, 420, 1), 'velocidade')
        cadencia = ctrl.Antecedent(np.arange(0, 120, 1), 'cadencia')
        comprimento_do_passo = ctrl.Antecedent(
            np.arange(0, 90, 1), 'comprimento_do_passo')
        largura_da_passada = ctrl.Antecedent(
            np.arange(0, 60, 1), 'largura_da_passada')
        comprimento_medio_da_passada = ctrl.Antecedent(
            np.arange(0, 140, 1), 'comprimento_medio_da_passada')
        angulo_flexao_joelho_esquerdo = ctrl.Antecedent(
            np.arange(0, 90, 1), 'angulo_flexao_joelho_esquerdo')
        angulo_flexao_joelho_direito = ctrl.Antecedent(
            np.arange(0, 90, 1), 'angulo_flexao_joelho_direito')
        angulo_extensao_do_quadril = ctrl.Antecedent(
            np.arange(-45, 45, 1), 'angulo_extensao_do_quadril')
        angulo_abertura_entre_as_pernas = ctrl.Antecedent(
            np.arange(0, 45, 1), 'angulo_abertura_entre_as_pernas')
        simetria_passo = ctrl.Antecedent(
            np.arange(0, 100, 1), 'simetria_passo')
        movimento = ctrl.Consequent(np.arange(0, 6, 1), 'movimento')

        velocidade['normal_time_up'] = fuzz.trimf(
            velocidade.universe, [137.09879, 172.5753, 208.0518])
        velocidade['normal_linha_reta'] = fuzz.trimf(
            velocidade.universe, [138.816, 169.129, 199.4246])
        velocidade['normal_circulos'] = fuzz.trimf(
            velocidade.universe, [138.816, 141.0000714, 144.4246])
        velocidade['normal_elevacao_excessiva'] = fuzz.trimf(
            velocidade.universe, [138.4224973, 175.92612, 208.0518])
        velocidade['normal_assimetria'] = fuzz.trimf(
            velocidade.universe, [125.4260833, 159.4321, 193.4381167])
        velocidade['normal_circundacao_do_pe'] = fuzz.trimf(
            velocidade.universe, [136.7154148, 156.9547586, 177.1971025])
        # Cria as funções de pertinência usando tipos variados\n",
        cadencia['normal_time_up'] = fuzz.trimf(
            cadencia.universe, [38.25736, 52.0326, 65.8079])
        cadencia['normal_circulos'] = fuzz.trimf(
            cadencia.universe, [49.44284, 65.312564, 81.18228])
        cadencia['normal_linha_reta'] = fuzz.trimf(
            cadencia.universe, [44.74271219, 57.39628, 70.04985])
        cadencia['normal_elevacao_excessiva'] = fuzz.trimf(
            cadencia.universe, [38.51748809, 48.76656549, 59.0156429])
        cadencia['normal_assimetria'] = fuzz.trimf(
            cadencia.universe, [27.29257307, 36.30009, 45.30760693])
        cadencia['normal_circundacao_do_pe'] = fuzz.trimf(
            cadencia.universe, [35.27988115, 48.881937, 62.48399333])

        comprimento_do_passo['normal_time_up'] = fuzz.trimf(
            comprimento_do_passo.universe, [38.25736, 52.0326, 65.8079])
        comprimento_do_passo['normal_circulos'] = fuzz.trimf(
            comprimento_do_passo.universe, [49.44284, 65.312564, 81.18228])
        comprimento_do_passo['normal_linha_reta'] = fuzz.trimf(
            comprimento_do_passo.universe, [44.74271219, 57.39628, 70.04985])
        comprimento_do_passo['normal_elevacao_excessiva'] = fuzz.trimf(
            comprimento_do_passo.universe, [38.51748809, 48.76656549, 59.0156429])
        comprimento_do_passo['normal_assimetria'] = fuzz.trimf(
            comprimento_do_passo.universe, [27.29257307, 36.30009, 45.30760693])
        comprimento_do_passo['normal_circundacao_do_pe'] = fuzz.trimf(
            comprimento_do_passo.universe, [35.27988115, 48.881937, 62.48399333])

        largura_da_passada['normal_time_up'] = fuzz.trimf(
            largura_da_passada.universe, [13.6656, 18.744167, 23.8227])
        largura_da_passada['normal_circulos'] = fuzz.trimf(
            largura_da_passada.universe, [17.834049, 21.20535, 24.576664])
        largura_da_passada['normal_linha_reta'] = fuzz.trimf(
            largura_da_passada.universe, [10.287206, 14.883193, 17.89432])
        largura_da_passada['normal_elevacao_excessiva'] = fuzz.trimf(
            largura_da_passada.universe, [12.0939295, 14.922323, 17.750718])
        largura_da_passada['normal_assimetria'] = fuzz.trimf(
            largura_da_passada.universe, [11.0075071, 14.3783, 17.749041])
        largura_da_passada['normal_circundacao_do_pe'] = fuzz.trimf(
            largura_da_passada.universe, [16.7906, 20.30275, 23.814912222])

        comprimento_medio_da_passada['normal_time_up'] = fuzz.trimf(
            comprimento_medio_da_passada.universe, [72.920965, 93.3905, 113.8600342])
        comprimento_medio_da_passada['normal_circulos'] = fuzz.trimf(
            comprimento_medio_da_passada.universe, [80.57295, 94.49942857, 108.4259])
        comprimento_medio_da_passada['normal_linha_reta'] = fuzz.trimf(
            comprimento_medio_da_passada.universe, [82.25978, 102.495042, 122.730299])
        comprimento_medio_da_passada['normal_elevacao_excessiva'] = fuzz.trimf(
            comprimento_medio_da_passada.universe, [85.351901, 101.6935211, 118.0851247])
        comprimento_medio_da_passada['normal_assimetria'] = fuzz.trimf(
            comprimento_medio_da_passada.universe, [84.0207071, 104.8706, 125.53412])
        comprimento_medio_da_passada['normal_circundacao_do_pe'] = fuzz.trimf(
            comprimento_medio_da_passada.universe, [85.09882699, 101.9391724, 118.7795178])

        angulo_flexao_joelho_esquerdo['normal_time_up'] = fuzz.trimf(
            angulo_flexao_joelho_esquerdo.universe, [13.81809171, 25.30216731, 36.7862429])
        angulo_flexao_joelho_esquerdo['normal_circulos'] = fuzz.trimf(
            angulo_flexao_joelho_esquerdo.universe, [10.64351894, 13.52068478, 16.39785065])
        angulo_flexao_joelho_esquerdo['normal_linha_reta'] = fuzz.trimf(
            angulo_flexao_joelho_esquerdo.universe, [14.6545624, 19.060428, 23.46629464])
        angulo_flexao_joelho_esquerdo['normal_elevacao_excessiva'] = fuzz.trimf(
            angulo_flexao_joelho_esquerdo.universe, [15.818338108, 19.63514299, 22.91190484])
        angulo_flexao_joelho_esquerdo['normal_assimetria'] = fuzz.trimf(
            angulo_flexao_joelho_esquerdo.universe, [12.62910062, 16.609454, 20.54980738])
        angulo_flexao_joelho_esquerdo['normal_circundacao_do_pe'] = fuzz.trimf(
            angulo_flexao_joelho_esquerdo.universe, [12.92773617, 15.97714297, 19.02655176])

        angulo_flexao_joelho_direito['normal_time_up'] = fuzz.trimf(
            angulo_flexao_joelho_direito.universe, [13.89057, 26.056837, 39.49550034])
        angulo_flexao_joelho_direito['normal_circulos'] = fuzz.trimf(
            angulo_flexao_joelho_direito.universe, [9.29664711, 13.14893524, 17.00122337])
        angulo_flexao_joelho_direito['normal_linha_reta'] = fuzz.trimf(
            angulo_flexao_joelho_direito.universe, [15.55603103, 18.28713686, 21.0182468])
        angulo_flexao_joelho_direito['normal_elevacao_excessiva'] = fuzz.trimf(
            angulo_flexao_joelho_direito.universe, [18.66268024, 26.390742, 34.11880424])
        angulo_flexao_joelho_direito['normal_assimetria'] = fuzz.trimf(
            angulo_flexao_joelho_direito.universe, [13.93655161, 17.19679528, 20.45723894])
        angulo_flexao_joelho_direito['normal_circundacao_do_pe'] = fuzz.trimf(
            angulo_flexao_joelho_direito.universe, [8.765121565, 11.87795929, 14.99079702])

        angulo_extensao_do_quadril['normal_time_up'] = fuzz.trimf(
            angulo_extensao_do_quadril.universe, [-23.15779296, -12.29735485, -1.436916])
        angulo_extensao_do_quadril['normal_circulos'] = fuzz.trimf(
            angulo_extensao_do_quadril.universe, [-6.146797956, -2.470977127, 1.204843702])
        angulo_extensao_do_quadril['normal_linha_reta'] = fuzz.trimf(
            angulo_extensao_do_quadril.universe, [-12.41980411, -5.200609834, 2.018584444])
        angulo_extensao_do_quadril['normal_elevacao_excessiva'] = fuzz.trimf(
            angulo_extensao_do_quadril.universe, [-15.7359458, -7.974425723, -0.2129056])
        angulo_extensao_do_quadril['normal_assimetria'] = fuzz.trimf(
            angulo_extensao_do_quadril.universe, [-12.40705176, -2.70631406, 6.994423644])
        angulo_extensao_do_quadril['normal_circundacao_do_pe'] = fuzz.trimf(
            angulo_extensao_do_quadril.universe, [-11.63432389, -2.285577901, 7.063168084])

        angulo_abertura_entre_as_pernas['normal_time_up'] = fuzz.trimf(
            angulo_abertura_entre_as_pernas.universe, [10.93681242, 15.50976667, 20.08272091])
        angulo_abertura_entre_as_pernas['normal_circulos'] = fuzz.trimf(
            angulo_abertura_entre_as_pernas.universe, [12.26088281, 14.12320857, 15.98553433])
        angulo_abertura_entre_as_pernas['normal_linha_reta'] = fuzz.trimf(
            angulo_abertura_entre_as_pernas.universe, [13.76452914, 17.70428235, 21.64403557])
        angulo_abertura_entre_as_pernas['normal_elevacao_excessiva'] = fuzz.trimf(
            angulo_abertura_entre_as_pernas.universe, [13.9617069, 17.35211056, 20.74251944])
        angulo_abertura_entre_as_pernas['normal_assimetria'] = fuzz.trimf(
            angulo_abertura_entre_as_pernas.universe, [13.75063875, 17.215808, 20.68097725])
        angulo_abertura_entre_as_pernas['normal_circundacao_do_pe'] = fuzz.trimf(
            angulo_abertura_entre_as_pernas.universe, [13.57704299, 16.86888897, 20.16073494])

        simetria_passo['normal_time_up'] = fuzz.trimf(
            simetria_passo.universe, [42.867734, 64.816799, 86.765])
        simetria_passo['normal_circulos'] = fuzz.trimf(
            simetria_passo.universe, [57.93206288, 77.00225705, 96.07245122])
        simetria_passo['normal_linha_reta'] = fuzz.trimf(
            simetria_passo.universe, [56.68912292, 79.30667771, 100.6272325])
        simetria_passo['normal_elevacao_excessiva'] = fuzz.trimf(
            simetria_passo.universe, [59.12070059, 77.44019057, 95.75968054])
        simetria_passo['normal_assimetria'] = fuzz.trimf(
            simetria_passo.universe, [53.14273563, 71.66624849, 99.18976134])
        simetria_passo['normal_circundacao_do_pe'] = fuzz.trimf(
            simetria_passo.universe, [60.39012182, 77.8415655, 95.29300928])

        movimento['Time Up and Go'] = fuzz.trimf(movimento.universe, [0, 0, 1])
        movimento['Círculos'] = fuzz.trimf(movimento.universe, [0, 1, 2])
        movimento['Em linha reta'] = fuzz.trimf(movimento.universe, [1, 2, 3])
        movimento['Elevação excessiva'] = fuzz.trimf(
            movimento.universe, [2, 3, 4])
        movimento['Assimetria'] = fuzz.trimf(movimento.universe, [3, 4, 5])
        movimento['Circundacao do pe'] = fuzz.trapmf(
            movimento.universe, [4, 5, 6, 7])

        # Deveria ser um dicionário ou lista???
        rule1 = ctrl.Rule(
            velocidade['normal_time_up'] & cadencia['normal_time_up'] & comprimento_do_passo['normal_time_up'] &
            largura_da_passada['normal_time_up'] & comprimento_medio_da_passada['normal_time_up'] &
            angulo_flexao_joelho_esquerdo['normal_time_up']
            & angulo_flexao_joelho_direito['normal_time_up'] | angulo_extensao_do_quadril['normal_time_up'] &
            angulo_abertura_entre_as_pernas['normal_time_up'] | simetria_passo['normal_time_up'],
            movimento['Time Up and Go'])
        rule2 = ctrl.Rule(
            velocidade['normal_circulos'] & cadencia['normal_circulos'] & comprimento_do_passo['normal_circulos'] &
            largura_da_passada['normal_circulos'] & comprimento_medio_da_passada['normal_circulos'] &
            angulo_flexao_joelho_esquerdo['normal_circulos']
            & angulo_flexao_joelho_direito['normal_circulos'] & angulo_extensao_do_quadril['normal_circulos'] &
            angulo_abertura_entre_as_pernas['normal_circulos'] & simetria_passo['normal_circulos'],
            movimento['Círculos'])
        rule3 = ctrl.Rule(
            velocidade['normal_elevacao_excessiva'] & cadencia['normal_elevacao_excessiva'] & comprimento_do_passo[
                'normal_elevacao_excessiva'] & largura_da_passada['normal_elevacao_excessiva'] &
            comprimento_medio_da_passada['normal_elevacao_excessiva'] & angulo_flexao_joelho_esquerdo[
                'normal_elevacao_excessiva']
            & angulo_flexao_joelho_direito['normal_elevacao_excessiva'] & angulo_extensao_do_quadril[
                'normal_elevacao_excessiva'] & angulo_abertura_entre_as_pernas['normal_elevacao_excessiva'] &
            simetria_passo['normal_elevacao_excessiva'], movimento['Elevação excessiva'])
        rule4 = ctrl.Rule(velocidade['normal_assimetria'] & cadencia['normal_assimetria'] & comprimento_do_passo[
            'normal_assimetria'] & largura_da_passada['normal_assimetria'] & comprimento_medio_da_passada[
            'normal_assimetria'] & angulo_flexao_joelho_esquerdo['normal_assimetria']
            & angulo_flexao_joelho_direito['normal_assimetria'] & angulo_extensao_do_quadril[
            'normal_assimetria'] & angulo_abertura_entre_as_pernas['normal_assimetria'] &
            simetria_passo['normal_assimetria'], movimento['Assimetria'])
        rule5 = ctrl.Rule(
            velocidade['normal_circundacao_do_pe'] & cadencia['normal_circundacao_do_pe'] & comprimento_do_passo[
                'normal_circundacao_do_pe'] & largura_da_passada['normal_circundacao_do_pe'] &
            comprimento_medio_da_passada['normal_circundacao_do_pe'] & angulo_flexao_joelho_esquerdo[
                'normal_circundacao_do_pe']
            & angulo_flexao_joelho_direito['normal_circundacao_do_pe'] & angulo_extensao_do_quadril[
                'normal_circundacao_do_pe'] & angulo_abertura_entre_as_pernas['normal_circundacao_do_pe'] &
            simetria_passo['normal_circundacao_do_pe'], movimento['Circundacao do pe'])
        rule6 = ctrl.Rule(velocidade['normal_linha_reta'] & cadencia['normal_linha_reta'] & comprimento_do_passo[
            'normal_linha_reta'] & largura_da_passada['normal_linha_reta'] & comprimento_medio_da_passada[
            'normal_linha_reta'] & angulo_flexao_joelho_esquerdo['normal_linha_reta']
            & angulo_flexao_joelho_direito['normal_linha_reta'] & angulo_extensao_do_quadril[
            'normal_linha_reta'] & angulo_abertura_entre_as_pernas['normal_linha_reta'] &
            simetria_passo['normal_linha_reta'], movimento['Em linha reta'])
        rule7 = ctrl.Rule(
            velocidade['normal_assimetria'] & cadencia['normal_linha_reta'] & comprimento_do_passo['normal_time_up'] &
            largura_da_passada['normal_circundacao_do_pe'] & comprimento_medio_da_passada['normal_time_up'] &
            angulo_flexao_joelho_esquerdo['normal_time_up'] & angulo_flexao_joelho_direito['normal_time_up'] &
            angulo_abertura_entre_as_pernas['normal_time_up'] & angulo_extensao_do_quadril['normal_time_up'] &
            simetria_passo['normal_linha_reta'], movimento['Time Up and Go'])
        rule8 = ctrl.Rule(
            velocidade['normal_time_up'] & cadencia['normal_time_up'] & comprimento_do_passo['normal_time_up'] &
            largura_da_passada['normal_time_up'] &
            comprimento_medio_da_passada['normal_time_up'] & angulo_flexao_joelho_esquerdo['normal_time_up'] &
            angulo_flexao_joelho_direito['normal_time_up'], movimento['Time Up and Go'])
        rule9 = ctrl.Rule(
            velocidade['normal_time_up'] & cadencia['normal_time_up'] & comprimento_do_passo['normal_time_up']
            & largura_da_passada['normal_time_up'] & simetria_passo['normal_time_up'], movimento['Time Up and Go'])
        rule10 = ctrl.Rule(
            velocidade['normal_circulos'] & cadencia['normal_circulos'] & comprimento_do_passo['normal_circulos'] &
            largura_da_passada['normal_circulos'] & comprimento_medio_da_passada['normal_circulos'] & simetria_passo[
                'normal_circulos'], movimento['Círculos'])
        rule11 = ctrl.Rule(
            velocidade['normal_circulos'] & cadencia['normal_circulos'] & comprimento_do_passo['normal_circulos']
            & largura_da_passada['normal_circulos'] & simetria_passo['normal_circulos'], movimento['Círculos'])
        rule12 = ctrl.Rule(
            velocidade['normal_circulos'] & cadencia['normal_circulos'] & comprimento_do_passo['normal_circulos'] &
            largura_da_passada['normal_circulos'] & angulo_flexao_joelho_esquerdo['normal_circulos']
            & angulo_flexao_joelho_direito['normal_circulos'] & angulo_extensao_do_quadril['normal_circulos'] &
            angulo_abertura_entre_as_pernas['normal_circulos'] & simetria_passo['normal_circulos'],
            movimento['Círculos'])
        rule13 = ctrl.Rule(velocidade['normal_linha_reta'] & cadencia['normal_linha_reta'] & comprimento_do_passo[
            'normal_linha_reta'] & largura_da_passada['normal_linha_reta'] & comprimento_medio_da_passada[
            'normal_linha_reta']
            & angulo_flexao_joelho_esquerdo['normal_linha_reta'] & angulo_flexao_joelho_direito[
            'normal_linha_reta'] & angulo_extensao_do_quadril['normal_linha_reta'] & simetria_passo[
            'normal_linha_reta'], movimento['Em linha reta'])
        rule14 = ctrl.Rule(velocidade['normal_linha_reta'] & cadencia['normal_linha_reta'] & comprimento_do_passo[
            'normal_linha_reta'] & largura_da_passada['normal_linha_reta'] &
            comprimento_medio_da_passada['normal_linha_reta'] & angulo_flexao_joelho_esquerdo[
            'normal_linha_reta'] & angulo_flexao_joelho_direito['normal_linha_reta'],
            movimento['Em linha reta'])
        rule15 = ctrl.Rule(
            velocidade['normal_linha_reta'] & cadencia['normal_linha_reta'] & comprimento_do_passo['normal_linha_reta']
            & largura_da_passada['normal_linha_reta'] & simetria_passo['normal_linha_reta'], movimento['Em linha reta'])
        rule16 = ctrl.Rule(velocidade['normal_assimetria'] & cadencia['normal_assimetria'] & comprimento_do_passo[
            'normal_assimetria'] & largura_da_passada['normal_assimetria'] & comprimento_medio_da_passada[
            'normal_assimetria']
            & angulo_flexao_joelho_esquerdo['normal_assimetria'] & angulo_flexao_joelho_direito[
            'normal_assimetria'] & angulo_extensao_do_quadril['normal_assimetria'] & simetria_passo[
            'normal_assimetria'], movimento['Assimetria'])
        rule17 = ctrl.Rule(velocidade['normal_assimetria'] & cadencia['normal_assimetria'] & comprimento_do_passo[
            'normal_assimetria'] & largura_da_passada['normal_assimetria'] &
            comprimento_medio_da_passada['normal_assimetria'] & angulo_flexao_joelho_esquerdo[
            'normal_assimetria'] & angulo_flexao_joelho_direito['normal_assimetria'],
            movimento['Assimetria'])
        rule18 = ctrl.Rule(
            velocidade['normal_assimetria'] & cadencia['normal_assimetria'] & comprimento_do_passo['normal_assimetria']
            & largura_da_passada['normal_assimetria'] & simetria_passo['normal_assimetria'], movimento['Assimetria'])
        rule19 = ctrl.Rule(
            velocidade['normal_elevacao_excessiva'] & cadencia['normal_elevacao_excessiva'] & comprimento_do_passo[
                'normal_elevacao_excessiva'] & largura_da_passada['normal_elevacao_excessiva'] &
            comprimento_medio_da_passada['normal_elevacao_excessiva']
            & angulo_flexao_joelho_esquerdo['normal_elevacao_excessiva'] & angulo_flexao_joelho_direito[
                'normal_elevacao_excessiva'] & angulo_extensao_do_quadril['normal_elevacao_excessiva'] & simetria_passo[
                'normal_elevacao_excessiva'], movimento['Elevação excessiva'])
        rule20 = ctrl.Rule(
            velocidade['normal_elevacao_excessiva'] & cadencia['normal_elevacao_excessiva'] & comprimento_do_passo[
                'normal_elevacao_excessiva'] & largura_da_passada['normal_elevacao_excessiva'] &
            comprimento_medio_da_passada['normal_elevacao_excessiva'] & angulo_flexao_joelho_esquerdo[
                'normal_elevacao_excessiva'] & angulo_flexao_joelho_direito['normal_elevacao_excessiva'],
            movimento['Elevação excessiva'])
        rule21 = ctrl.Rule(
            velocidade['normal_elevacao_excessiva'] & cadencia['normal_elevacao_excessiva'] & comprimento_do_passo[
                'normal_elevacao_excessiva']
            & largura_da_passada['normal_elevacao_excessiva'] & simetria_passo['normal_elevacao_excessiva'],
            movimento['Elevação excessiva'])
        rule22 = ctrl.Rule(
            velocidade['normal_circundacao_do_pe'] & cadencia['normal_circundacao_do_pe'] & comprimento_do_passo[
                'normal_circundacao_do_pe'] & largura_da_passada['normal_circundacao_do_pe'] &
            comprimento_medio_da_passada['normal_circundacao_do_pe']
            & angulo_flexao_joelho_esquerdo['normal_circundacao_do_pe'] & angulo_flexao_joelho_direito[
                'normal_circundacao_do_pe'] & angulo_extensao_do_quadril['normal_circundacao_do_pe'] & simetria_passo[
                'normal_circundacao_do_pe'], movimento['Circundacao do pe'])
        rule23 = ctrl.Rule(
            velocidade['normal_circundacao_do_pe'] & cadencia['normal_circundacao_do_pe'] & comprimento_do_passo[
                'normal_circundacao_do_pe'] & largura_da_passada['normal_circundacao_do_pe'] &
            comprimento_medio_da_passada['normal_circundacao_do_pe'] & angulo_flexao_joelho_esquerdo[
                'normal_circundacao_do_pe'] & angulo_flexao_joelho_direito['normal_circundacao_do_pe'],
            movimento['Circundacao do pe'])
        rule24 = ctrl.Rule(
            velocidade['normal_circundacao_do_pe'] & cadencia['normal_circundacao_do_pe'] & comprimento_do_passo[
                'normal_circundacao_do_pe']
            & largura_da_passada['normal_circundacao_do_pe'] & simetria_passo['normal_circundacao_do_pe'],
            movimento['Circundacao do pe'])
        rule25 = ctrl.Rule(
            velocidade['normal_time_up'] & cadencia['normal_time_up'] & comprimento_do_passo['normal_time_up'] &
            largura_da_passada['normal_time_up']
            & angulo_abertura_entre_as_pernas['normal_time_up'] & simetria_passo['normal_time_up'],
            movimento['Time Up and Go'])
        rule26 = ctrl.Rule(
            velocidade['normal_circulos'] & cadencia['normal_circulos'] & comprimento_do_passo['normal_circulos'] &
            largura_da_passada['normal_circulos'] & comprimento_medio_da_passada['normal_circulos']
            & angulo_flexao_joelho_direito['normal_circulos'] & angulo_extensao_do_quadril['normal_circulos'] &
            angulo_abertura_entre_as_pernas['normal_circulos'] & simetria_passo['normal_circulos'],
            movimento['Círculos'])
        rule27 = ctrl.Rule(cadencia['normal_circulos'] & comprimento_do_passo['normal_circulos'] & largura_da_passada[
            'normal_circulos'] & comprimento_medio_da_passada['normal_circulos'] &
            angulo_flexao_joelho_esquerdo['normal_circulos'] & angulo_flexao_joelho_direito[
            'normal_circulos'] & angulo_extensao_do_quadril['normal_circulos'] & simetria_passo[
            'normal_circulos'], movimento['Círculos'])
        rule28 = ctrl.Rule(
            cadencia['normal_circulos'] & largura_da_passada['normal_circulos'] & comprimento_medio_da_passada[
                'normal_circulos']
            & angulo_extensao_do_quadril['normal_circulos'] & simetria_passo['normal_circulos'], movimento['Círculos'])
        rule29 = ctrl.Rule(
            velocidade['normal_assimetria'] & cadencia['normal_circundacao_do_pe'] & comprimento_do_passo[
                'normal_circundacao_do_pe'] & largura_da_passada['normal_time_up'] & comprimento_medio_da_passada[
                'normal_circulos'] &
            angulo_flexao_joelho_esquerdo['normal_circulos'] & angulo_flexao_joelho_direito['normal_circulos'] &
            angulo_extensao_do_quadril['normal_circundacao_do_pe'] & angulo_abertura_entre_as_pernas['normal_time_up'] &
            simetria_passo['normal_linha_reta'], movimento['Círculos'])
        rule30 = ctrl.Rule(velocidade['normal_time_up'] & cadencia['normal_circundacao_do_pe'] & comprimento_do_passo[
            'normal_circundacao_do_pe'] & largura_da_passada['normal_linha_reta'] & comprimento_medio_da_passada[
            'normal_circulos'] &
            angulo_flexao_joelho_esquerdo['normal_circulos'] & angulo_flexao_joelho_direito[
            'normal_circulos'] & angulo_extensao_do_quadril['normal_assimetria'] &
            angulo_abertura_entre_as_pernas['normal_time_up'] & simetria_passo['normal_assimetria'],
            movimento['Círculos'])
        rule31 = ctrl.Rule(
            velocidade['normal_assimetria'] & cadencia['normal_circundacao_do_pe'] & comprimento_do_passo[
                'normal_assimetria'] & largura_da_passada['normal_elevacao_excessiva'] & comprimento_medio_da_passada[
                'normal_circulos'] & angulo_flexao_joelho_esquerdo['normal_circundacao_do_pe']
            & angulo_flexao_joelho_direito['normal_circundacao_do_pe'] & angulo_extensao_do_quadril[
                'normal_circundacao_do_pe'] & angulo_abertura_entre_as_pernas['normal_time_up'] & simetria_passo[
                'normal_linha_reta'], movimento['Círculos'])
        rule32 = ctrl.Rule(velocidade['normal_time_up'] & cadencia['normal_circundacao_do_pe'] & comprimento_do_passo[
            'normal_circundacao_do_pe'] & largura_da_passada['normal_linha_reta'] & angulo_flexao_joelho_esquerdo[
            'normal_circulos']
            & angulo_flexao_joelho_direito['normal_circundacao_do_pe'] & angulo_extensao_do_quadril[
            'normal_circundacao_do_pe'] & angulo_abertura_entre_as_pernas['normal_time_up'] &
            simetria_passo['normal_time_up'], movimento['Círculos'])
        rule33 = ctrl.Rule(cadencia['normal_circundacao_do_pe'] & comprimento_do_passo['normal_circundacao_do_pe'] &
                           largura_da_passada['normal_linha_reta'] & angulo_abertura_entre_as_pernas['normal_time_up'],
                           movimento['Em linha reta'])
        rule34 = ctrl.Rule(cadencia['normal_circundacao_do_pe'] & comprimento_do_passo['normal_circundacao_do_pe']
                           & largura_da_passada['normal_time_up'] & simetria_passo['normal_assimetria'],
                           movimento['Círculos'])
        rule35 = ctrl.Rule(velocidade['normal_linha_reta'] & cadencia['normal_circulos'] &
                           angulo_flexao_joelho_esquerdo['normal_circulos'] & angulo_flexao_joelho_direito[
                               'normal_circulos'], movimento['Círculos'])
        rule36 = ctrl.Rule(
            velocidade['normal_linha_reta'] & cadencia['normal_circulos'] & angulo_flexao_joelho_esquerdo[
                'normal_circulos'] & angulo_flexao_joelho_direito['normal_circulos']
            & angulo_extensao_do_quadril['normal_linha_reta'] | angulo_abertura_entre_as_pernas[
                'normal_circundacao_do_pe'] & simetria_passo['normal_linha_reta'], movimento['Círculos'])
        rule37 = ctrl.Rule(
            velocidade['normal_assimetria'] & cadencia['normal_time_up'] & comprimento_do_passo['normal_time_up'] &
            largura_da_passada['normal_circundacao_do_pe'] & comprimento_medio_da_passada['normal_time_up'] &
            angulo_flexao_joelho_esquerdo['normal_time_up']
            & angulo_flexao_joelho_direito['normal_time_up'] & angulo_abertura_entre_as_pernas['normal_time_up'] |
            angulo_extensao_do_quadril['normal_time_up'] | simetria_passo['normal_linha_reta'],
            movimento['Time Up and Go'])
        rule38 = ctrl.Rule(
            velocidade['normal_circundacao_do_pe'] & cadencia['normal_linha_reta'] & comprimento_do_passo[
                'normal_time_up'] & largura_da_passada['normal_circundacao_do_pe'] & comprimento_medio_da_passada[
                'normal_time_up'] &
            angulo_flexao_joelho_esquerdo['normal_time_up'] & angulo_flexao_joelho_direito['normal_time_up'] &
            angulo_abertura_entre_as_pernas['normal_time_up'] & angulo_extensao_do_quadril['normal_time_up'] |
            simetria_passo['normal_linha_reta'], movimento['Time Up and Go'])
        rule39 = ctrl.Rule(
            velocidade['normal_circundacao_do_pe'] & cadencia['normal_linha_reta'] & comprimento_do_passo[
                'normal_time_up'] & largura_da_passada['normal_circundacao_do_pe']
            & comprimento_medio_da_passada['normal_time_up'] & angulo_extensao_do_quadril['normal_time_up'] &
            simetria_passo['normal_linha_reta'], movimento['Time Up and Go'])
        rule40 = ctrl.Rule(
            velocidade['normal_linha_reta'] & cadencia['normal_linha_reta'] & comprimento_do_passo['normal_time_up'] &
            largura_da_passada['normal_linha_reta'] & comprimento_medio_da_passada['normal_time_up']
            & angulo_abertura_entre_as_pernas['normal_time_up'] & angulo_extensao_do_quadril[
                'normal_elevacao_excessiva'] & simetria_passo['normal_linha_reta'], movimento['Time Up and Go'])
        rule41 = ctrl.Rule(
            cadencia['normal_assimetria'] & comprimento_do_passo['normal_circundacao_do_pe'] & largura_da_passada[
                'normal_circundacao_do_pe'] &
            angulo_flexao_joelho_direito['normal_circundacao_do_pe'] & angulo_extensao_do_quadril[
                'normal_elevacao_excessiva'] | simetria_passo['normal_linha_reta'], movimento['Circundacao do pe'])
        rule42 = ctrl.Rule(
            cadencia['normal_assimetria'] & comprimento_do_passo['normal_circundacao_do_pe'] & largura_da_passada[
                'normal_time_up'] &
            angulo_flexao_joelho_direito['normal_circundacao_do_pe'] & angulo_extensao_do_quadril['normal_assimetria'],
            movimento['Circundacao do pe'])
        rule43 = ctrl.Rule(
            cadencia['normal_assimetria'] & comprimento_do_passo['normal_circundacao_do_pe'] & largura_da_passada[
                'normal_time_up'] & angulo_flexao_joelho_esquerdo['normal_circulos'] &
            angulo_flexao_joelho_direito['normal_circulos'] & angulo_abertura_entre_as_pernas['normal_time_up'] &
            angulo_extensao_do_quadril['normal_elevacao_excessiva'], movimento['Circundacao do pe'])
        rule44 = ctrl.Rule(
            cadencia['normal_assimetria'] & comprimento_do_passo['normal_circundacao_do_pe'] & largura_da_passada[
                'normal_time_up'] & angulo_flexao_joelho_direito['normal_circulos']
            & angulo_abertura_entre_as_pernas['normal_time_up'] & angulo_extensao_do_quadril[
                'normal_elevacao_excessiva'], movimento['Circundacao do pe'])
        rule45 = ctrl.Rule(
            cadencia['normal_assimetria'] & comprimento_do_passo['normal_circundacao_do_pe'] & largura_da_passada[
                'normal_time_up'] & angulo_flexao_joelho_esquerdo['normal_circulos']
            & angulo_abertura_entre_as_pernas['normal_time_up'] & angulo_extensao_do_quadril[
                'normal_elevacao_excessiva'], movimento['Circundacao do pe'])
        rule46 = ctrl.Rule(comprimento_do_passo['normal_circundacao_do_pe'] & largura_da_passada['normal_linha_reta'] &
                           angulo_flexao_joelho_esquerdo['normal_circulos'] &
                           angulo_flexao_joelho_direito['normal_time_up'] & angulo_abertura_entre_as_pernas[
                               'normal_time_up'] & simetria_passo['normal_linha_reta'], movimento['Em linha reta'])
        rule47 = ctrl.Rule(comprimento_do_passo['normal_circundacao_do_pe'] & largura_da_passada['normal_linha_reta'] &
                           angulo_flexao_joelho_esquerdo['normal_circulos'] &
                           angulo_flexao_joelho_direito['normal_time_up'] & angulo_abertura_entre_as_pernas[
                               'normal_linha_reta'] & simetria_passo['normal_linha_reta'], movimento['Em linha reta'])
        rule48 = ctrl.Rule(comprimento_do_passo['normal_time_up'] & largura_da_passada['normal_linha_reta'] &
                           angulo_flexao_joelho_esquerdo['normal_time_up'] &
                           angulo_flexao_joelho_direito['normal_time_up'] & angulo_abertura_entre_as_pernas[
                               'normal_time_up'] & simetria_passo['normal_assimetria'], movimento['Time Up and Go'])
        rule49 = ctrl.Rule(velocidade['normal_assimetria'] & cadencia['normal_assimetria'] &
                           comprimento_do_passo['normal_circundacao_do_pe'] & simetria_passo['normal_time_up'],
                           movimento['Time Up and Go'])
        rule50 = ctrl.Rule(angulo_flexao_joelho_esquerdo['normal_circundacao_do_pe'] & angulo_flexao_joelho_direito[
            'normal_circulos'] & angulo_abertura_entre_as_pernas['normal_time_up'], movimento['Time Up and Go'])
        rule51 = ctrl.Rule(comprimento_do_passo['normal_circundacao_do_pe'] & angulo_abertura_entre_as_pernas[
            'normal_linha_reta'] & simetria_passo['normal_assimetria'], movimento['Time Up and Go'])
        rule52 = ctrl.Rule(
            simetria_passo['normal_time_up'], movimento['Time Up and Go'])
        rule53 = ctrl.Rule(comprimento_do_passo['normal_circundacao_do_pe'] & largura_da_passada['normal_circulos'] &
                           angulo_flexao_joelho_esquerdo['normal_assimetria'] & angulo_flexao_joelho_direito[
                               'normal_time_up'], movimento['Time Up and Go'])
        rule54 = ctrl.Rule(cadencia['normal_assimetria'] &
                           largura_da_passada['normal_circulos'], movimento['Circundacao do pe'])

        # movimento_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
        # rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23,
        # rule24,rule25, rule26, rule27, rule28, rule29, rule30, rule31, rule32, rule33, rule34, rule35,
        # rule36]) movimento_ctrl = ctrl.ControlSystem([rule1, rule2, rule5, rule6, rule7, rule22, rule23, rule24,
        # rule25, rule26, rule27, rule28, rule29, rule30, rule31, rule32, rule33, rule34, rule35, rule36, rule37])
        movimento_ctrl = ctrl.ControlSystem(
            [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14,
             rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26,
             rule27, rule28, rule29, rule30, rule31, rule32, rule33, rule34, rule35, rule36, rule37, rule38, rule39,
             rule40, rule41, rule42, rule43, rule44, rule45, rule46, rule47, rule48, rule49, rule50, rule51, rule52,
             rule53, rule54])
        movimento_simulador = ctrl.ControlSystemSimulation(movimento_ctrl)

        # ???
        # Entrando com alguns valores para qualidade da comida e do serviço
        movimento_simulador.input['velocidade'] = velocidade_media * 100
        movimento_simulador.input['cadencia'] = cadencia_medido
        movimento_simulador.input['largura_da_passada'] = (
            statistics.mean(largura_media) * 100)
        movimento_simulador.input['comprimento_do_passo'] = (
            statistics.mean(comprimento_passo_medido) * 100)
        movimento_simulador.input['comprimento_medio_da_passada'] = (
            statistics.mean(comprimento_medio_passada))
        movimento_simulador.input['angulo_flexao_joelho_esquerdo'] = statistics.mean(
            flexion_left_knee_angle)
        movimento_simulador.input['angulo_flexao_joelho_direito'] = statistics.mean(
            flexion_right_knee_angle)
        movimento_simulador.input['angulo_extensao_do_quadril'] = statistics.mean(
            ang_ext_quadril)
        movimento_simulador.input['angulo_abertura_entre_as_pernas'] = statistics.mean(
            aux_angulo)
        movimento_simulador.input['simetria_passo'] = (
            simetria_comprimento_passo[-1]) * 100

        print(velocidade_media * 100, cadencia_medido, (statistics.mean(largura_media) * 100),
              (statistics.mean(comprimento_passo_medido) *
               100), (statistics.mean(comprimento_medio_passada)),
              statistics.mean(flexion_left_knee_angle), statistics.mean(
                  flexion_right_knee_angle),
              statistics.mean(ang_ext_quadril), statistics.mean(aux_angulo), (simetria_comprimento_passo[-1]) * 100)
        # Computando o resultado
        movimento_simulador.compute()
        resultado = movimento_simulador.output['movimento']

        # Aparentemente salva os resultados em imagem
        velocidade.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/velocidade.png')
        cadencia.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/cadencia.png')
        comprimento_do_passo.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/comprimento_do_passo.png')
        largura_da_passada.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/largura_da_passada.png')
        comprimento_medio_da_passada.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/comprimento_medio_da_passada.png')
        angulo_flexao_joelho_esquerdo.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/angulo_flexao_joelho_esquerdo.png')
        angulo_flexao_joelho_direito.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/angulo_flexao_joelho_direito.png')
        angulo_extensao_do_quadril.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/angulo_extensao_quadril.png')
        angulo_abertura_entre_as_pernas.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/angulo_de_abertura.png')
        simetria_passo.view(sim=movimento_simulador)
        plt.savefig(options.folder + '/simetria.png')

        print(resultado)
        try:
            if resultado < 1:
                print("Time Up and Go")
            elif (resultado >= 1) and (resultado < 2):
                print("Em círculos")
            elif (resultado >= 2) and (resultado < 3):
                print("Em linha reta")
            elif (resultado >= 3) and (resultado < 4):
                print("Elevação do calcanhar")
            elif (resultado >= 5) and (resultado < 6):
                print("Assimetria de passo")
            else:
                print("Circundação do pé")
        except:
            print("Movimento não reconhecido")
        # print(resultado)
        return resultado

    @staticmethod
    def altura_da_pessoa(skeletons):
        """_summary_

        Args:
            skeletons (_type_): _description_

        Returns:
            float: _description_
        """
        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
        altura_da_pessoa = 0
        for skeletons in skeletons_pb.objects:
            parts = {}
            for part in skeletons.keypoints:
                parts[part.id] = (
                    part.position.x, part.position.y, part.position.z)
                if part.id == 1:
                    altura_da_pessoa = parts[1]
            if altura_da_pessoa:
                altura_da_pessoa = parts[1][2]
            else:
                altura_da_pessoa = 0
            break
        return altura_da_pessoa

    @staticmethod
    def angulo_caminhada(perna_direita, perna_esquerda, picos_distancia, altura_quadril):
        """_summary_

        Args:
            perna_direita (_type_): _description_
            perna_esquerda (_type_): _description_
            picos_distancia (_type_): _description_
            altura_quadril (_type_): _description_

        Returns:
            _type_: _description_
        """
        teta_angulo_dist_entre_pes = []
        # Não usados???
        '''k = 0
        aux_perna_direita = perna_direita
        aux_perna_esquerda = perna_esquerda'''
        aux1_cosseno = aux2_cosseno = 0
        # print(len(picos_distancia))
        for k in range(len(picos_distancia)):
            # 2*(aux_perna_direita[k])*(aux_perna_esquerda[k])
            A = altura_quadril
            if A != 0:
                # aux1_cosseno=(aux_perna_direita[k])**2+(aux_perna_esquerda[k])**2-(picos_distancia[k])**2
                # aux2_cosseno=aux1_cosseno/A
                aux1_cosseno = (picos_distancia[k])
            else:
                A = 1
            if aux1_cosseno <= 1:
                # teta_angulo_dist_entre_pes.append(math.degrees(math.acos(aux2_cosseno)))
                teta_angulo_dist_entre_pes.append(
                    math.degrees(math.atan(aux1_cosseno / A)))
            else:
                teta_angulo_dist_entre_pes.append(0)

            # print(teta_angulo_dist_entre_pes[k])
            # print(k)
            # k=k+1
        # print((teta_angulo_dist_entre_pes))
        return teta_angulo_dist_entre_pes

    # Estou usando apenas este atualmente para conseguir o angulo durante a caminhada
    @staticmethod
    def angulo_caminhada_real(perna_direita, perna_esquerda, distance_feet):
        """_summary_

        Args:
            perna_direita (_type_): _description_
            perna_esquerda (_type_): _description_
            distance_feet (_type_): _description_

        Returns:
            _type_: _description_
        """
        angulo = 0
        # print(distance_feet)
        B = pow(distance_feet, 2) - \
            (pow(perna_esquerda, 2) + pow(perna_direita, 2))
        A = -2 * perna_direita * perna_esquerda

        if (A != 0) and (B / A) < 1:
            angulo = math.degrees(math.acos(B / A))

        else:
            angulo = 0
        return angulo

    @staticmethod
    def left_knee_angle(skeletons):
        """_summary_

        Args:
            skeletons (_type_): _description_

        Returns:
            _type_: _description_
        """
        left_ankle = left_hip = left_knee = None

        aux_left_leg = None
        left_knee_angle = 0
        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())

        for skeletons in skeletons_pb.objects:
            parts = {}
            for part in skeletons.keypoints:
                parts[part.id] = (
                    part.position.x, part.position.y, part.position.z)

                if part.id == 13:
                    left_hip = parts[13]
                if part.id == 14:
                    left_knee = parts[14]
                if part.id == 15:
                    left_ankle = parts[15]
            if left_ankle and left_hip and left_knee:
                left_hip = parts[13]
                left_knee = parts[14]
                left_ankle = parts[15]

                # a,b,c ???

                a = np.sqrt((left_ankle[0] - left_knee[0]) ** 2 + (left_ankle[1] -
                                                                   left_knee[1]) ** 2 + (
                    left_ankle[2] - left_knee[2]) ** 2)
                b = np.sqrt((left_knee[0] - left_hip[0]) ** 2 + (left_knee[1] -
                                                                 left_hip[1]) ** 2 + (left_knee[2] - left_hip[2]) ** 2)
                c = np.sqrt((left_hip[0] - left_ankle[0]) ** 2 + (left_hip[1] -
                                                                  left_ankle[1]) ** 2 + (
                    left_hip[2] - left_ankle[2]) ** 2)
                B = pow(c, 2) - (pow(a, 2) + pow(b, 2))
                A = -2 * b * c
                if A != 0:
                    if (B / A) < 1:
                        left_knee_angle = math.degrees(math.acos(B / A))
                else:
                    left_knee_angle = 0
            else:
                left_knee_angle = 0
        return left_knee_angle

    @staticmethod
    def file_maker(cam_id, juntas, perdidas, juntas_3d, perdidas_3d, average_height, idade, porcentagem, porcentagem_3d,
                   perda_media, variancia, y, x, perna_esquerda, perna_direita, maior_passo_medido, tempo_total,
                   velocidade_media, passos_por_min, contador, tempo_total_em_min, dist_do_chao, comprimento_passo_real,
                   Stance_real, Swing_real, distance_feet, dist_dos_pes_inicial, picos_distancia,
                   comprimento_passo_medido, comprimento_swing, comprimento_stance, angulo, altura_quadril,
                   left_knee_angle, angulo_real_joelho_esquerdo, comprimento_passo_real_medido, flexion_left_knee,
                   simetria_comprimento_passo, largura_da_passada, ang_ext_quadril):
        """_summary_

        Args:
            cam_id (_type_): _description_
            juntas (_type_): _description_
            perdidas (_type_): _description_
            juntas_3d (_type_): _description_
            perdidas_3d (_type_): _description_
            average_height (_type_): _description_
            idade (_type_): _description_
            porcentagem (_type_): _description_
            porcentagem_3d (_type_): _description_
            perda_media (_type_): _description_
            variancia (_type_): _description_
            y (_type_): _description_
            x (_type_): _description_
            perna_esquerda (_type_): _description_
            perna_direita (_type_): _description_
            maior_passo_medido (_type_): _description_
            tempo_total (_type_): _description_
            velocidade_media (_type_): _description_
            passos_por_min (_type_): _description_
            contador (_type_): _description_
            tempo_total_em_min (_type_): _description_
            dist_do_chao (_type_): _description_
            comprimento_passo_real (_type_): _description_
            Stance_real (_type_): _description_
            Swing_real (_type_): _description_
            distance_feet (_type_): _description_
            dist_dos_pes_inicial (_type_): _description_
            picos_distancia (_type_): _description_
            comprimento_passo_medido (_type_): _description_
            comprimento_swing (_type_): _description_
            comprimento_stance (_type_): _description_
            angulo (_type_): _description_
            altura_quadril (_type_): _description_
            left_knee_angle (_type_): _description_
            angulo_real_joelho_esquerdo (_type_): _description_
            comprimento_passo_real_medido (_type_): _description_
            flexion_left_knee (_type_): _description_
            simetria_comprimento_passo (_type_): _description_
            largura_da_passada (_type_): _description_
            ang_ext_quadril (_type_): _description_
        """

        file_results = open(
            options.folder + "/Resultados_reconstrucao_3D.txt", "w")
        file_results.write("Resultados da reconstrução 3D \n")
        for cam_id in range(0, 4):
            porcentagem = (perdidas[cam_id] / juntas[cam_id]) * 100
            file_results.write("cam{}: Juntas detectadas: {} | Perdidas: {} |  {:.2f} %".format(
                cam_id, juntas[cam_id], perdidas[cam_id], porcentagem))
            file_results.write("\n")

        file_results.write("Juntas detectadas [Serviço 3d]: {} | Perdidas: {} |  {:.2f} %".format(
            juntas_3d, perdidas_3d, porcentagem_3d))
        file_results.write("\n")
        file_results.write(
            "Média das medições das perdas no 3D: %5.2f" % perda_media + " %")
        file_results.write("\n")
        file_results.write(
            "Variância das medições das perdas no 3D: %5.2f" % variancia + " %")
        file_results.write("\n")
        file_results.write(
            "Desvio padrão das medições das perdas no 3D: %5.2f" % statistics.pstdev(y) + " %")
        file_results.write("\n")
        altura_media = sum(average_height) / len(x)
        file_results.write("Altura média: %5.3f m" % altura_media)
        file_results.write("\n")
        file_results.write("Idade: %.3s anos" % idade)
        file_results.write("\n")
        perna_esquerda_media = sum(
            perna_esquerda) / len(perna_esquerda) + statistics.mean(dist_do_chao)
        file_results.write("Perna esquerda: %5.3f m" % perna_esquerda_media)
        file_results.write("\n")
        perna_direita_media = sum(
            perna_direita) / len(perna_direita) + statistics.mean(dist_do_chao)
        file_results.write("Perna direita: %5.3f m" % perna_direita_media)
        file_results.write("\n")
        file_results.write("Maior comprimento de passo: %.3f m" %
                           maior_passo_medido)
        file_results.write("\n")
        file_results.write("Tempo total: %5.4f" % tempo_total)
        file_results.write("\n")
        file_results.write("Tempo de suporte duplo: %.3f s " %
                           (0.2 * tempo_total))
        file_results.write("\n")
        file_results.write("Velocidade média: %.3f m/s " % velocidade_media)
        file_results.write("\n")
        file_results.write("Número de passos: %d " % contador)
        file_results.write("\n")
        file_results.write("Cadência (passos por min): %.3f " % passos_por_min)
        file_results.write("\n")
        vetor_erro_comprimento_de_passo = []
        vetor_erro_comprimento_de_meio_passo = []
        vetor_erro_comprimento_swing = []
        vetor_erro_comprimento_stance = []
        vetor_erro_distancia_dos_pes_inicial = []
        dist = []
        dist.append(dist_dos_pes_inicial)
        dist.append(distance_feet[0])

        comprimento_medio_real_de_meio_passo = (Stance_real + Swing_real) / 2
        erro_medio_comprimento_de_passo = comprimento_passo_real_medido - \
            statistics.mean(comprimento_passo_medido)

        # Deveria ser generator
        for j in range(0, len(comprimento_passo_medido)):
            vetor_erro_comprimento_de_passo.append(
                abs(comprimento_passo_real - comprimento_passo_medido[j]))

        for i in range(0, len(picos_distancia)):
            vetor_erro_comprimento_de_meio_passo.append(
                abs(comprimento_medio_real_de_meio_passo - picos_distancia[i]))

        for j in range(0, len(comprimento_stance)):
            vetor_erro_comprimento_stance.append(
                abs(Stance_real - comprimento_stance[j]))

        for j in range(0, len(comprimento_swing)):
            vetor_erro_comprimento_swing.append(
                abs(Swing_real - comprimento_swing[j]))

        for j in range(0, len(dist)):
            vetor_erro_distancia_dos_pes_inicial.append(
                abs(dist_dos_pes_inicial - dist[j]))

        # print("Erro stride")
        # print(vetor_erro_comprimento_de_passo)

        # print("Erro comprimento de meio passo")
        # print(vetor_erro_comprimento_de_meio_passo)

        erro_medio_comprimento_da_passada = (
            comprimento_passo_real_medido - statistics.mean(comprimento_passo_medido))
        erro_medio_meio_comprimento_de_passo = (
            comprimento_medio_real_de_meio_passo - statistics.mean(picos_distancia))

        # ???

        file_results.write("Comprimento médio da passada: %.4f m " %
                           (statistics.mean(comprimento_passo_medido)))
        file_results.write("\n")
        file_results.write("Erro médio do comprimento da passada: %.3f m" %
                           erro_medio_comprimento_da_passada)
        file_results.write("\n")
        file_results.write("Desvio padrão do comprimento médio da passada: %.3f m" %
                           statistics.pstdev(comprimento_passo_medido))
        file_results.write("\n")
        file_results.write("Comprimento médio do passo: %.4f m " %
                           (statistics.mean(picos_distancia)))
        file_results.write("\n")
        file_results.write("Erro médio do comprimento da passada: %.3f m" %
                           erro_medio_meio_comprimento_de_passo)
        file_results.write("\n")
        file_results.write("Desvio padrão do comprimento médio do passo: %.3f m" %
                           statistics.pstdev(picos_distancia))
        erro_swing = Swing_real - statistics.mean(comprimento_swing)
        file_results.write("\n")
        file_results.write("Desvio padrão do erro de comprimento do passo em %.3f m" %
                           statistics.pstdev(vetor_erro_comprimento_de_meio_passo))
        file_results.write("\n")
        file_results.write("Largura de passo: %.3f " %
                           statistics.mean(largura_da_passada))
        file_results.write("\n")
        file_results.write("Erro da largura de passo: %.3f " % (
            dist_dos_pes_inicial - statistics.mean(largura_da_passada)))
        file_results.write("\n")
        file_results.write("Desvio padrão da largura de passo: %.3f" %
                           statistics.pstdev(largura_da_passada))
        file_results.write("\n")
        file_results.write("Comprimento do Swing: %.4f m " %
                           statistics.mean(comprimento_swing))
        file_results.write("\n")
        file_results.write("Erro médio do Swing: %.3f m" % erro_swing)
        file_results.write("\n")
        file_results.write("Desvio padrão do Swing: %.3f m" %
                           statistics.pstdev(comprimento_swing))
        file_results.write("\n")
        file_results.write("Desvio padrão do erro de swing em %.4f m " %
                           statistics.pstdev(vetor_erro_comprimento_swing))
        erro_stance = Stance_real - statistics.mean(comprimento_stance)
        file_results.write("\n")
        file_results.write("Comprimento do Stance: %.4f m " %
                           statistics.mean(comprimento_stance))
        file_results.write("\n")
        file_results.write("Erro médio do stance: %.3f m" % erro_stance)
        file_results.write("\n")
        file_results.write("Desvio padrão do stance: %.3f m" %
                           statistics.pstdev(comprimento_stance))
        file_results.write("\n")
        file_results.write("Desvio padrão do erro de stance em %.4f m" %
                           statistics.pstdev(vetor_erro_comprimento_stance))
        file_results.write("\n")
        file_results.write("Comprimento médio Stride: %.4f m " %
                           statistics.mean(comprimento_passo_medido))
        file_results.write("\n")
        file_results.write("Erro médio do Stride:: %.3f m" %
                           erro_medio_comprimento_de_passo)
        file_results.write("\n")
        file_results.write("Desvio padrão  Stride: %.3f m" %
                           statistics.pstdev(comprimento_passo_medido))
        file_results.write("\n")
        file_results.write("Desvio padrão do erro do Stride em %.3f m" %
                           statistics.pstdev(vetor_erro_comprimento_de_passo))

        erro_dist_inicial = dist_dos_pes_inicial - \
            statistics.mean(largura_da_passada)
        file_results.write("\n")
        file_results.write("Distância inicial do pé: %.3f m " %
                           dist_dos_pes_inicial)
        file_results.write("\n")
        file_results.write(
            "Erro médio da distância entre os pés: %.3f m " % erro_dist_inicial)
        file_results.write("\n")
        file_results.write(
            "Desvio padrão da distância inicial entre os pés: %.3f m " % statistics.pstdev(dist))
        file_results.write("\n")
        file_results.write("Desvio padrão do erro da distância inicial entre os pés em %.4f m" %
                           statistics.pstdev(vetor_erro_distancia_dos_pes_inicial))
        file_results.write("\n")
        file_results.write(
            "Ângulo médio entre as pernas durante a caminhada em graus: %.3f " % statistics.mean(angulo))
        file_results.write("\n")
        c = altura_quadril
        b = altura_quadril
        a = Stance_real
        aux = (pow(c, 2) + pow(b, 2)) - pow(a, 2)
        aux2 = aux / (2 * b * c)
        # erro_medio_angulo=math.degrees(math.acos(aux2))-statistics.mean(angulo) file_results.write("Erro médio,
        # em graus, do angulo entre as pernas durante a caminhada: %.3f " % abs(erro_medio_angulo))
        # file_results.write("\n")
        file_results.write("Desvio padrão do ângulo médio entre as pernas durante a caminhada em graus: %.3f " % abs(
            statistics.pstdev(angulo)))
        file_results.write("\n")
        file_results.write("Ângulo da coxa do joelho da perna esquerda: %.3f graus" % abs(
            statistics.mean(left_knee_angle)))
        file_results.write("\n")
        file_results.write("Erro do angulo da coxa do joelho da perna esquerda: %.3f graus" % (
            angulo_real_joelho_esquerdo - (statistics.mean(left_knee_angle))))
        file_results.write("\n")
        file_results.write("Desvio padrão do ângulo da coxa do joelho esquerdo: %.3f graus" % (
            statistics.pstdev(left_knee_angle)))
        file_results.write("\n")
        file_results.write("Ângulo de flexão do joelho esquerdo: %.3f ° " %
                           statistics.mean(flexion_left_knee))
        file_results.write("\n")
        file_results.write("Desvio padrão do ângulo de flexão do joelho esquerdo: %.3f °" %
                           statistics.pstdev(flexion_left_knee))
        file_results.write("\n")
        file_results.write("Ângulo extensão do quadril direito: %.3f °" %
                           statistics.mean(ang_ext_quadril))
        file_results.write("\n")
        file_results.write("Desvio padrão do ângulo de extensão do quadril: %.3f º" %
                           statistics.pstdev(ang_ext_quadril))
        file_results.write("\n")
        file_results.write("Simetria do comprimento de passo: %.3f" %
                           statistics.mean(simetria_comprimento_passo))
        file_results.write("\n")
        file_results.write("Desvio padrão da simetria do comprimento de passo %.3f" %
                           statistics.pstdev(simetria_comprimento_passo))
        file_results.close()

    @staticmethod
    def file_maker_csv(comprimento_passo_real_medido, cadencia, Stance_real, Swing_real, distance_feet,
                       dist_dos_pes_inicial, picos_distancia, comprimento_passo_medido, comprimento_swing,
                       comprimento_stance, aux_angulo, altura_quadril, idade, velocidade_media, perna_direita,
                       altura_real, left_knee_angle, angulo_real_joelho_esquerdo, sexo, flexion_left_knee,
                       flexion_right_knee, simetria_comprimento_passo, largura_da_passada, ang_ext_quadril,
                       left_extension_hip_angle, right_extension_hip_angle, movimento, CAPTURA,
                       quant_de_ciclos_desejado):
        """_summary_

        Args:
            comprimento_passo_real_medido (_type_): _description_
            cadencia (_type_): _description_
            Stance_real (_type_): _description_
            Swing_real (_type_): _description_
            distance_feet (_type_): _description_
            dist_dos_pes_inicial (_type_): _description_
            picos_distancia (_type_): _description_
            comprimento_passo_medido (_type_): _description_
            comprimento_swing (_type_): _description_
            comprimento_stance (_type_): _description_
            aux_angulo (_type_): _description_
            altura_quadril (_type_): _description_
            idade (_type_): _description_
            velocidade_media (_type_): _description_
            perna_direita (_type_): _description_
            altura_real (_type_): _description_
            left_knee_angle (_type_): _description_
            angulo_real_joelho_esquerdo (_type_): _description_
            sexo (_type_): _description_
            flexion_left_knee (_type_): _description_
            flexion_right_knee (_type_): _description_
            simetria_comprimento_passo (_type_): _description_
            largura_da_passada (_type_): _description_
            ang_ext_quadril (_type_): _description_
            left_extension_hip_angle (_type_): _description_
            right_extension_hip_angle (_type_): _description_
            movimento (_type_): _description_
            CAPTURA (_type_): _description_
            quant_de_ciclos_desejado (_type_): _description_
        """

        # ???
        #    with open(options.folder+"/Parâmetros.csv", 'w') as csvfile:
        #      filewriter = csv.writer(csvfile, delimiter=',',
        #                         quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #      filewriter.writerow(["Nº do parâmetro","Parâmetros", "Valores"])
        #      filewriter.writerow(["0",'Altura em metros', '%.2f' % statistics.mean(average_height)])
        #      vetor_erro_comprimento_de_passo=[]
        #      vetor_erro_comprimento_de_meio_passo=[]
        #      vetor_erro_comprimento_swing=[]
        #      vetor_erro_comprimento_stance=[]
        #      vetor_erro_distancia_dos_pes_inicial=[]
        #      dist=[]
        #      dist.append(dist_dos_pes_inicial)
        #      dist.append(distance_feet[0])

        #      comprimento_medio_real_de_meio_passo=(Stance_real+Swing_real)/2
        #      erro_medio_comprimento_de_passo=comprimento_passo_real-statistics.mean(comprimento_passo_medido)

        #      for j in range(0,len(comprimento_passo_medido)):
        #         vetor_erro_comprimento_de_passo.append(abs(comprimento_passo_real-comprimento_passo_medido[j]))

        #      for i in range(0,len(picos_distancia)):
        #         vetor_erro_comprimento_de_meio_passo.append(abs(comprimento_medio_real_de_meio_passo-picos_distancia[i]))

        #      for j in range(0,len(comprimento_stance)):
        #         vetor_erro_comprimento_stance.append(abs(Stance_real-comprimento_stance[j]))

        #      for j in range(0,len(comprimento_swing)):
        #         vetor_erro_comprimento_swing.append(abs(Swing_real-comprimento_swing[j]))

        #      for j in range(0,len(dist)):
        #         vetor_erro_distancia_dos_pes_inicial.append(abs(dist_dos_pes_inicial-dist[j]))
        #     # print("Erro stride")
        #     # print(vetor_erro_comprimento_de_passo)

        #     # print("Erro comprimento de meio passo")
        #     # print(vetor_erro_comprimento_de_meio_passo)

        # erro_medio_meio_comprimento_de_passo=(comprimento_medio_real_de_meio_passo - statistics.mean(
        # picos_distancia)) filewriter.writerow(["1","Comprimento médio de passo em metros",
        # "%.4f" % statistics.mean(comprimento_passo_medido)]) filewriter.writerow(["2","Erro absoluto médio do
        # comprimento de passo em metros","%.4f" % abs(erro_medio_comprimento_de_passo)]) filewriter.writerow(["3",
        # "Desvio padrão comprimento passo medido em metros", "%.4f" % abs(statistics.pstdev(
        # comprimento_passo_medido))]) filewriter.writerow(["4","Desvio padrão do erro de comprimento de passo em
        # metros", " %.2f" % abs(statistics.pstdev(vetor_erro_comprimento_de_passo))]) filewriter.writerow(["5",
        # "Comprimento médio de meio passo em metros","%.4f" % statistics.mean(picos_distancia)])
        # filewriter.writerow(["6","Erro absoluto médio do meio comprimento de passo em metros", "%.4f" % abs(
        # erro_medio_meio_comprimento_de_passo)]) filewriter.writerow(["7","Desvio padrão do comprimento médio de
        # meio passo em metros", "%.4f"% abs(statistics.pstdev(picos_distancia))]) erro_swing=
        # Swing_real-statistics.mean(comprimento_swing) filewriter.writerow(["8","Desvio padrão do erro de
        # comprimento de meio passo em metros","%.4f" % abs(statistics.pstdev(
        # vetor_erro_comprimento_de_meio_passo))]) filewriter.writerow(["9","Comprimento do Swing em metros",
        # " %.4f" % statistics.mean(comprimento_swing)]) filewriter.writerow(["10","Erro absoluto médio do swing em
        # metros","%.4f" % abs(erro_swing)]) filewriter.writerow(["11","Desvio padrão do swing em metros",
        # "%.4f" % abs(statistics.pstdev(comprimento_swing))]) filewriter.writerow(["12","Desvio padrão do erro de
        # swing em metros","%.4f" % abs(statistics.pstdev(vetor_erro_comprimento_swing))]) erro_stance=
        # Stance_real-statistics.mean(comprimento_stance) filewriter.writerow(["13","Comprimento do Stance em
        # metros:","%.4f" % statistics.mean(comprimento_stance)]) filewriter.writerow(["14","Erro absoluto médio do
        # stance em metros"," %.4f" % abs(erro_stance)]) filewriter.writerow(["15","Desvio padrão do stance em
        # metros", "%.4f " % abs(statistics.pstdev(comprimento_stance))]) filewriter.writerow(["16","Desvio padrão do
        # erro de stance em metros","%.4f" % abs(statistics.pstdev(vetor_erro_comprimento_stance))])
        # erro_dist_inicial=dist_dos_pes_inicial - distance_feet[0] filewriter.writerow(["17","Distância inicial do
        # pé em metros","%.4f" % distance_feet[0]]) filewriter.writerow(["18","Erro absoluto médio da distância entre
        # os pés em metros"," %.4f" % abs(erro_dist_inicial)]) filewriter.writerow(["19","Desvio padrão da distância
        # inicial entre os pés"," %.4f" % abs(statistics.pstdev(dist))]) filewriter.writerow(["20","Desvio padrão do
        # erro da distância inicial entre os pés em metros","%.4f" % abs(statistics.pstdev(
        # vetor_erro_distancia_dos_pes_inicial))]) c=altura_quadril b=altura_quadril #print(c) #print(b)
        # a=Stance_real #print(c) aux=(pow(c,2)+pow(b,2))-pow(a,2) aux2=aux/(2*b*c) erro_medio_angulo=math.degrees(
        # math.acos(aux2))-statistics.mean(angulo_caminhada) filewriter.writerow(["21","Ângulo real de abertura das
        # pernas em graus", "%.4f" % math.degrees(math.acos(aux2))]) #print(math.degrees(math.acos(aux2))) #print(
        # math.degrees(math.acos(((2*((altura_quadril)**2)-Stance_real)/(2*((statistics.mean(perna_direita))**2))))))
        # filewriter.writerow(["22","Ângulo médio de abertura das pernas em graus", "%.4f" % statistics.mean(
        # angulo_caminhada)]) filewriter.writerow(["23","Erro absoluto médio do angulo entre as pernas em graus",
        # "%5.4f" % abs(erro_medio_angulo)]) filewriter.writerow(["24","Desvio padrão do ângulo médio dos passos em
        # graus", "%5.4f" % abs(statistics.pstdev(angulo_caminhada))]) filewriter.writerow(["25","Número de amostras
        # do ângulo","%i" % len(angulo_caminhada)])
        vetor_erro_comprimento_de_passo = []
        vetor_erro_comprimento_de_meio_passo = []
        vetor_erro_comprimento_swing = []
        vetor_erro_comprimento_stance = []
        vetor_erro_distancia_dos_pes_inicial = []
        dist = []
        dist.append(dist_dos_pes_inicial)
        dist.append(distance_feet[0])

        comprimento_medio_real_de_meio_passo = (Stance_real + Swing_real) / 2
        erro_medio_comprimento_de_passo = statistics.pstdev(
            comprimento_passo_medido)

        # ???
        # Repete muitas vezes
        for j in range(len(comprimento_passo_medido)):
            vetor_erro_comprimento_de_passo.append(
                abs(comprimento_passo_real_medido - comprimento_passo_medido[j]))

        for i in range(len(picos_distancia)):
            vetor_erro_comprimento_de_meio_passo.append(
                abs(comprimento_medio_real_de_meio_passo - picos_distancia[i]))

        for j in range(len(comprimento_stance)):
            vetor_erro_comprimento_stance.append(
                abs(Stance_real - comprimento_stance[j]))

        for j in range(len(comprimento_swing)):
            vetor_erro_comprimento_swing.append(
                abs(Swing_real - comprimento_swing[j]))

        for j in range(len(dist)):
            vetor_erro_distancia_dos_pes_inicial.append(
                abs(dist_dos_pes_inicial - dist[j]))

        erro_swing = Swing_real - statistics.mean(comprimento_swing)
        erro_stance = Stance_real - statistics.mean(comprimento_stance)
        erro_medio_meio_comprimento_de_passo = (
            comprimento_medio_real_de_meio_passo - statistics.mean(picos_distancia))
        # erro_dist_inicial=dist_dos_pes_inicial - distance_feet[0]
        b = c = altura_quadril
        a = Stance_real
        # print(c)
        aux = (pow(c, 2) + pow(b, 2)) - pow(a, 2)
        aux2 = aux / (2 * b * c)
        data = time.strftime("%Y%m%d")
        # erro_medio_angulo=math.degrees(math.acos(aux2))-statistics.mean(aux_angulo)
        # k=0

        # Deveria ter uma variável path
        with open(
                '/home/julian/docker/Pablo/CICLOS_v4/{}/{}/Parâmetros_de_todos_para_validacao_{}_ciclos_{}.csv'.format(
                    CAPTURA, quant_de_ciclos_desejado, quant_de_ciclos_desejado, CAPTURA), 'a') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # filewriter.writerow(["Altura (m)","Idade","Sexo","Velocidade média (m/s)", "Cadência","Comprimento médio passada", "Erro absoluto médio do comprimento de passo em metros","Desvio padrão comprimento passo medido em metros","Desvio padrão do erro de comprimento de passo em metros","Largura da passada","Erro largura da passada","Desvio padrão largura da passada","Comprimento médio de meio passo em metros","Erro absoluto médio do meio comprimento de passo em metros","Desvio padrão do comprimento médio de meio passo em metros","Desvio padrão do erro de comprimento de meio passo em metros","Comprimento do Swing em metros","Erro absoluto médio do swing em metros","Desvio padrão do swing em metros","Desvio padrão do erro de swing em metros","Comprimento do Stance em metros","Erro absoluto médio do stance em metros","Desvio padrão do stance em metros","Desvio padrão do erro de stance em metros","Distância inicial do pé em metros","Desvio padrão da distância inicial entre os pés","Ângulo médio de abertura das pernas durante a caminhada (°)","Desvio padrão do ângulo médio dos passos em graus","Número de amostras do ângulo","Ângulo médio da coxa do joelho esquerdo","Desvio padrão do ângulo  médio da coxa do joelho esquerdo","Ângulo médio de flexão do joelho esquerdo","Desvio padrão do ângulo de flexão do joelho esquerdo","Ângulo médio de flexão do joelho direito","Desvio padrão do ângulo de flexão do joelho direito","Ângulo extensão do quadril esquerdo (°)","Desvio padrão do ângulo de extensão do quadril esquerdo(°)","Ângulo extensão do quadril direito (°)","Desvio padrão do ângulo de extensão do quadril direito (°)","Simetria do comprimento de passo","Desvio padrão da simetria do comprimento de passo","Movimento"])
            filewriter.writerow(
                ["%.4f" % float(altura_real), "%.2f" % float(idade), "%i" % sexo, "%.4f" % velocidade_media,
                 "%.4f" % cadencia, "%.4f" % statistics.mean(
                     comprimento_passo_medido),
                 "%.4f" % abs(erro_medio_comprimento_de_passo),
                 "%.4f" % abs(statistics.pstdev(comprimento_passo_medido)),
                 " %.2f" % abs(statistics.pstdev(
                     vetor_erro_comprimento_de_passo)),
                 "%.4f" % statistics.mean(largura_da_passada),
                 "%.4f" % (dist_dos_pes_inicial -
                           statistics.mean(largura_da_passada)),
                 "%.4f" % statistics.pstdev(
                     largura_da_passada), "%.4f" % statistics.mean(picos_distancia),
                 "%.4f" % abs(erro_medio_meio_comprimento_de_passo), "%.4f" % abs(
                     statistics.pstdev(picos_distancia)),
                 "%.4f" % abs(statistics.pstdev(
                     vetor_erro_comprimento_de_meio_passo)),
                 " %.4f" % statistics.mean(
                     comprimento_swing), "%.4f" % abs(erro_swing),
                 "%.4f" % abs(statistics.pstdev(comprimento_swing)), "%.4f" % abs(statistics.pstdev(
                     vetor_erro_comprimento_swing)), "%.4f" % statistics.mean(comprimento_stance),
                 "%.4f" % abs(erro_stance), "%.4f " % abs(
                     statistics.pstdev(comprimento_stance)),
                 "%.4f" % abs(statistics.pstdev(vetor_erro_comprimento_stance)), "%.4f" % abs(
                     dist_dos_pes_inicial),
                 " %.4f" % abs(statistics.pstdev(
                     dist)), "%.4f" % statistics.mean(aux_angulo),
                 "%5.4f" % abs(statistics.pstdev(aux_angulo)), "%i" % len(
                     aux_angulo), statistics.mean(left_knee_angle),
                 statistics.pstdev(left_knee_angle), statistics.mean(
                     flexion_left_knee),
                 statistics.pstdev(flexion_left_knee), statistics.mean(
                     flexion_right_knee),
                 statistics.pstdev(flexion_right_knee), statistics.mean(
                     left_extension_hip_angle),
                 statistics.pstdev(left_extension_hip_angle), statistics.mean(
                     right_extension_hip_angle),
                 statistics.pstdev(right_extension_hip_angle), statistics.mean(
                     simetria_comprimento_passo),
                 statistics.pstdev(simetria_comprimento_passo), movimento])
            # k=k+1
            # print(len(angulo_caminhada))

    @staticmethod
    def Array_coordenadas(skeletons):
        """_summary_

        Args:
            skeletons (_type_): _description_

        Returns:
            _type_: _description_
        """
        skeletons_pb = ParseDict(skeletons, ObjectAnnotations())
        aux_array_coordenadas = []
        nome_das_coordenadas = []

        if skeletons_pb.objects:
            for skeletons in skeletons_pb.objects:
                parts = {}
                for part in skeletons.keypoints:
                    parts[part.id] = (
                        part.position.x, part.position.y, part.position.z)
                    nome_das_coordenadas = np.concatenate((nome_das_coordenadas, ("x_{}".format(
                        part.id), "y_{}".format(part.id), "z_{}".format(part.id))), axis=None)
                    aux_array_coordenadas = np.concatenate(
                        (aux_array_coordenadas, (part.position.x, part.position.y, part.position.z)), axis=None)
                    if len(aux_array_coordenadas) >= 45:
                        aux_array_coordenadas = aux_array_coordenadas[:45]
                        nome_das_coordenadas = nome_das_coordenadas[:45]
                if len(aux_array_coordenadas) < 45:
                    while len(aux_array_coordenadas) < 45:
                        aux_array_coordenadas = np.concatenate(
                            (aux_array_coordenadas, [0]), axis=None)

            nome_das_coordenadas = np.concatenate(
                (nome_das_coordenadas, ['Movimento']), axis=None)
        return aux_array_coordenadas, nome_das_coordenadas

    @staticmethod
    def write_json(data):
        try:
            to_unicode = unicode
        except NameError:
            to_unicode = str
        # with open(options.folder+'/data.json', 'w') as outfile:
        #    json.dump(data, ouqtfile)
        with io.open(options.folder + '/data.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data,
                              indent=4, sort_keys=False,
                              separators=(',', ': '), ensure_ascii=True)
            outfile.write(to_unicode(str_))

    @staticmethod
    def rede_neural(velocidade_media, comprimento_passo_medido, largura_da_passada, simetria_comprimento_passo,
                    cadencia):
        """_summary_

        Args:
            velocidade_media (_type_): _description_
            comprimento_passo_medido (_type_): _description_
            largura_da_passada (_type_): _description_
            simetria_comprimento_passo (_type_): _description_
            cadencia (_type_): _description_

        Returns:
            _type_: _description_
        """

        CATEGORIAS = ["Time Up and Go", "Em círculos", "Marcha em linha reta",
                      "Elevação excessiva do calcanhar", " Assimetria de passo", "Circundação do pé"]

        # ("/home/julian/docker/ifes-2019-09-09/Modelo_para_treinamento/Modelo_1/Modelo_detecta_caminhada")
        modelo_final = tf.keras.models.load_model(
            "/home/julian/docker/ifes-2019-09-09/Modelos_para_treinamento/Modelo_2/Modelo_detecta_caminhada_6_movimentos")
        input_values = [velocidade_media, comprimento_passo_medido,
                        largura_da_passada, simetria_comprimento_passo, cadencia]
        input_values = array(input_values)
        # print(input_values)
        # pt=preprocessing.PowerTransformer(method='box-cox',standardize=False)
        input_values = input_values.reshape([1, 5])  # ,bacth_size=32])
        # print(input_values)
        scaler = preprocessing.MinMaxScaler()  # preprocessing.normalize(input_values)
        input_values_normalize = scaler.fit_transform(input_values)
        # print(input_values_normalize)
        # input_values=(input_values/np.argmax(input_values))
        # input_values_normalize=pt.fit_transform(input_values)
        prediction = modelo_final.predict(input_values_normalize)
        # print(input_values_normalize)
        prediction = (np.around(prediction).reshape(1, 6))
        # print(prediction)
        # print(CATEGORIAS[np.argmax(prediction)])
        resultado = CATEGORIAS[np.argmax(prediction)]
        return resultado

    # def rede_neural_imagens(): CATEGORIES=["Certo","Errado"] filepath='0' img_array = cv2.imread(filepath,
    # cv2.IMREAD_GRAYSCALE) print(img_array) new_array = (cv2.resize(img_array, (IMG_SIZE, IMG_SIZE)))/255 print(
    # new_array.reshape(-1, IMG_SIZE, IMG_SIZE, 1)) modelo_final = tf.keras.models.load_model(
    # "/home/julian/docker/ifes-2019-09-09/Modelo_para_treinamento/Modelo_classificador_imagens
    # /Modelo_movimento_certo_e_errado_3")

    # prediction = model.predict([prepare('0')])
    # print(prediction)  # will be a list in a list.
    # print(CATEGORIES[int(prediction[0][0])])
    # if((CATEGORIES[int(prediction[0][0])])==0):
    #    return "Certo"

    # return "Errado"

    @staticmethod
    def prepare(filepath):
        """_summary_

        Args:
            filepath (_type_): _description_

        Returns:
            _type_: _description_
        """
        img_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
        return new_array.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

    @staticmethod
    def slide_gait_cycle(slide):
        # O que é???
        """_summary_

        Args:
            slide (_type_): _description_

        Returns:
            _type_: _description_
        """
        if slide in (0, 4):
            result = 4
        else:
            result = 2

        return result

    @staticmethod
    def prepara_split_do_array(array, quant_de_ciclos):
        """_summary_

        Args:
            array (_type_): _description_
            quant_de_ciclos (_type_): _description_

        Returns:
            _type_: _description_
        """
        div = len(array) // quant_de_ciclos
        ref_tamanho = quant_de_ciclos * div
        while len(array) != ref_tamanho:
            array = array[:-1]
        return array

    @staticmethod
    def normaliza_vetor(y, quant_de_ciclos, quant_de_ciclos_desejado, pico_do_sinal):
        """_summary_

        Args:
            y (_type_): _description_
            quant_de_ciclos (_type_): _description_
            quant_de_ciclos_desejado (_type_): _description_
            pico_do_sinal (_type_): _description_
        """

        # Essas referências podem mudar conforme os ciclos em interesse para análise!
        div = int(len(y) // quant_de_ciclos)  # Prepara para a quebra do array
        # Garante que haja somente múltiplos da quantidade de ciclos  para a normalização
        ref_tamanho = quant_de_ciclos * div

        # ???
        while len(y) != ref_tamanho:
            y.pop()

        y = np.array_split(y, quant_de_ciclos)

        y_refencia = y[-1]  # última medida por ciclo é pega como referência

        # for i in range (0,len(y_refencia)+1):
        # k_referencia.append((100*i)/len(y_refencia))

        for i in range(quant_de_ciclos_desejado - 1):
            a = np.array(y[i + 1])
            ultimo_elemento = a[-1]
            B = np.array([ultimo_elemento])
            y[i] = np.append(np.array(y[i]), B)

        if quant_de_ciclos_desejado == 1:  # S for de 1 ciclo a análise final fica com menor quantidade de dados pra
            # tirar a média
            y = [y[0]]
        else:
            y = y[:(quant_de_ciclos_desejado - 1)]

        # Alinhando as curvas
        aux_array = np.array(y[-1])
        # int(len(aux_array)*0.6) #np.argmax(aux_array) #
        indice_maior_valor = np.argmax(aux_array)

        for i in range(0, (len(y) - 1)):
            index_array_deslocado = np.argmax(y[i])
            while indice_maior_valor != (index_array_deslocado + 1):
                index_array_deslocado = np.argmax(y[i])
                y[i] = np.roll(y[i], 1)
                if not indice_maior_valor and not index_array_deslocado:
                    break

        aux = np.mean(y, axis=0)
        # print(len(y[0]),len(
        # k_referencia))
        # Limpa aux_array!
        aux_array = []
        indice_maior_valor = int(len(y_refencia) * (pico_do_sinal / 100.0))
        index_array_deslocado = np.argmax(aux)

        #### Alinhamento final!!!!!#####
        for i in range(len(y_refencia)):  # Array de referência !!!!!
            if i == indice_maior_valor:
                aux_array.append(1)
            else:
                aux_array.append(0)

        while indice_maior_valor != index_array_deslocado:
            index_array_deslocado = np.argmax(aux)
            aux = np.roll(aux, 1)

        return aux  # Vetor final após o processo de normalização

    @staticmethod
    def marca_frame(contador_numero_de_passos, frame):
        """_summary_

        Args:
            contador_numero_de_passos (_type_): _description_
            frame (_type_): _description_
        """

        BLUE = (255, 0, 0)
        RED = (0, 0, 255)
        if contador_numero_de_passos != 0:
            try:
                if contador_numero_de_passos % 2:
                    constant = cv2.copyMakeBorder(
                        frame, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=BLUE)
                else:
                    constant = cv2.copyMakeBorder(
                        frame, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=RED)
            except:
                pass
            # cv2.rectangle(display_image,(0,0),(510,128),(0,255,0),3)
        cv2.putText(frame, "Detecta passo", (1300, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, .4, (100, 00, 10), 1, cv2.LINE_AA)
        #cv2.imshow('Detector de passo', constant)
