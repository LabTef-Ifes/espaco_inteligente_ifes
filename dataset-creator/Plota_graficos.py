import os, re, sys, json, time, csv
import argparse
import numpy as np
import math, statistics
from sympy import S, symbols, printing
import matplotlib.pyplot as plt
from is_wire.core import Logger
from utils import load_options
from video_loader import MultipleVideoLoader

from collections import OrderedDict
log = Logger(name='WatchVideos')

with open('keymap.json') as f:
    keymap = json.load(f)
options = load_options(print_options=False)

# Classe sem self???
class Plota_graficos:
    @staticmethod
    def plota_grafico_perdas(y):
        """_summary_

        Args:
            y (_type_): _description_
        """        
        fig, AX = plt.subplots()
        # y=y[1:]
        X = []
        for i in range(0, len(y)):
            X.append(i)
        AX.plot(X, y)
        AX.set(xlabel='Medição', ylabel='Perda percentual (%)',
               title='Perdas na reconstrução 3D em função da amostragem')
        AX.grid()
        plt.savefig(options.folder + '/Perdas_na_reconstrucao3D.png')
        plt.show()

    @staticmethod
    def plota_grafico(y, title):
        fig, ax = plt.subplots()
        # y=y[1:]
        X = np.linspace(0, 100, num=len(y))

        ax.plot(X, y)
        ax.set(xlabel='N° de amostras', ylabel=title, title=title)
        ax.grid()
        plt.savefig(options.folder + '/' + title + '.png')
        plt.show()

    @staticmethod
    def plota_grafico_distance_feet(x, y):
        fig, ax = plt.subplots()
        y = y[2:]
        ax.plot(x, y)
        ax.set(xlabel='Tempo (s) ', ylabel='Distância (m) ', title='Medida das distâncias (m) em função do tempo (s)')
        ax.grid()
        plt.savefig(options.folder + '/Medidas_das_distancias_pelo_tempo.png')
        plt.show()

    @staticmethod
    def plota_grafico_tempo_de_passo(x, y, x_label='Tempo(s)', y_label='Comprimento(m)', titulo='Titulo'):
        """_summary_

        Args:
            x (_type_): _description_
            y (_type_): _description_
            x_label (str, optional): _description_. Defaults to 'Tempo(s)'.
            y_label (str, optional): _description_. Defaults to 'Comprimento(m)'.
            titulo (str, optional): _description_. Defaults to 'Titulo'.
        """        
        fig, ax = plt.subplots()
        # y=y[1:]
        ax.plot(x, y)
        ax.set(xlabel=x_label, ylabel=y_label, title=titulo)
        ax.grid()
        ax.plot(x, y)
        ax.set(xlabel=x_label, ylabel=y_label, title=titulo)
        ax.grid()
        plt.savefig(options.folder + '/Tempo_por_passo.png')
        plt.show()

    @staticmethod
    def plota_angulo_medido(y, titulo):
        """_summary_

        Args:
            y (_type_): _description_
            titulo (_type_): _description_
        """        
        k = list(range(len(y)))

        fig, ax = plt.subplots()
        ax.plot(k, y)
        ax.set(xlabel='N° de amostras', ylabel='Ângulo (°)', title=titulo)
        ax.grid()
        fig, ax = plt.subplots()
        ax.plot(k, y)
        ax.set(xlabel='N° de amostras', ylabel='Ângulo (°)', title=titulo)
        ax.grid()
        plt.savefig(options.folder + '/' + titulo + '.png')
        plt.show()

    @staticmethod
    def plota_simetria(y, titulo):
        """_summary_

        Args:
            y (_type_): _description_
            titulo (_type_): _description_
        """        
        k = list(range(len(y)))

        fig, ax = plt.subplots()
        ax.plot(k, y)
        ax.set(xlabel='N° de amostras', ylabel='Simetria', title=titulo)
        ax.grid()
        plt.savefig(options.folder + '/' + titulo + '.png')
        plt.show()

    @staticmethod
    def plota_angulo_medido_normalizado(y, titulo):
        """_summary_

        Args:
            y (_type_): _description_
            titulo (_type_): _description_
        """        
        #     k_referencia=[]

        # ## Essas referências podem mudar conforme os ciclos em interesse para análise !!!##
        #     y_refencia=y[-1]

        #    # for i in range (0,len(y_refencia)+1):
        #    #k_referencia.append((100*i)/len(y_refencia))

        #     for i in range(0,quant_de_ciclos_desejado-1):
        #         a=np.array(y[i+1])
        #         ultimo_elemento=a[-1]
        #         B=np.array([ultimo_elemento])
        #         y[i]=np.append(np.array(y[i]),B)

        #     if quant_de_ciclos_desejado==1: #S for de 1 ciclo a análise final fica com menor quantidade de dados pra tirar a média
        #         y=y[:(quant_de_ciclos_desejado)]

        #     y=y[:(quant_de_ciclos_desejado-1)]

        #     ##Alinhando as curvas
        #     index_array_deslocado=0
        #     aux_array=[]

        #     aux_array=np.array(y[-1])
        #     indice_maior_valor=np.argmax(aux_array) #int(len(aux_array)*0.6) #np.argmax(aux_array) #

        #     for i in range(0,quant_de_ciclos_desejado-1):
        #         index_array_deslocado=np.argmax(y[i])
        #         while ((indice_maior_valor) != (index_array_deslocado+1)):
        #             index_array_deslocado=np.argmax(y[i])
        #             y[i]=np.roll(y[i],1)
        #             if (indice_maior_valor==0 and index_array_deslocado==0):
        #                 #print("break")
        #                 break
        #     aux=[]
        #     aux=np.mean(y,axis=0)
        #     k_referencia=np.linspace(0, 100, num=len(aux))
        #     #print(len(y[0]),len(k_referencia))
        #     ### Limpa aux_array!
        #     aux_array=[]
        #     indice_maior_valor=int(len(y_refencia)*(pico_do_sinal/100.0))
        #     index_array_deslocado=np.argmax(aux)

        #     #### Alinhamento final!!!!!#####
        #     for i in range(0,len(y_refencia)): ## Array de referência !!!!!
        #         if (i ==indice_maior_valor):
        #             aux_array.append(1)
        #         else:
        #             aux_array.append(0)

        #     while ((indice_maior_valor) != (index_array_deslocado)):
        #             index_array_deslocado=np.argmax(aux)
        #             aux=np.roll(aux,1)

        k_referencia = np.linspace(0, 100, num=len(y))
        with open(options.folder + '/Parâmetros_de_todos_normalizado_' + titulo + '.csv', 'w') as myCsv:
            fieldnames = ["Gait Cycle (%)", "Angle (°)"]
            csvWriter = csv.DictWriter(myCsv, fieldnames=fieldnames)
            csvWriter.writeheader()
            for i in range(len(y)):
                csvWriter.writerow({'Gait Cycle (%)': '%.5f' % k_referencia[i], 'Angle (°)': '%.5f' % y[i]})
        fig, ax = plt.subplots()
        ax.plot(k_referencia, y, label="Valor médio: {:3f} +- {:3f}".format(statistics.mean(y), statistics.pstdev(y)),
                color="gray", linewidth=5.0, linestyle="--")

        # p & f ???
        p = np.polyfit(k_referencia, y, len(y) - 1)
        f = np.poly1d(p)
        xnew = k_referencia  # np.arange(0,len(y_refencia)+1)
        ynew = f(xnew)

        x = symbols("x")
        poly = sum(S("{:6.2f}".format(v)) * x ** i for i, v in enumerate(p[::-1]))
        eq_latex = printing.latex(poly)
        plt.plot(xnew, ynew, label="${}$".format(eq_latex))
        desvio_padrao_curva_media = np.std(y)
        Sigma_new_vec = desvio_padrao_curva_media  # ynew-aux
        lower_bound = y - Sigma_new_vec
        upper_bound = y + Sigma_new_vec
        # xnew = np.arange(0,100)
        plt.fill_between(xnew, lower_bound, upper_bound, color='green', alpha=.3)

        ax.set(xlabel='Gait Cycle %', ylabel='Angle (°)', title=titulo)
        ax.grid()
        plt.legend()
        plt.savefig(options.folder + '/' + titulo + '.png')
        plt.show()

    @staticmethod
    def trajetoria_vetor(vetor):
        """_summary_

        Args:
            vetor (_type_): _description_
        """        
        X, Y, Z = [0], [0], [0]

        title = 'Trajetória vetor normal ao tórax'
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.set_xlim3d([-2.0, 2.0])
        ax.set_xlabel('X')

        ax.set_ylim3d([-2.0, 2.0])
        ax.set_ylabel('Y')

        ax.set_zlim3d([-2.0, 2.0])
        ax.set_zlabel('Z')

        ax.set_title('Trajetória vetor normal ao tórax')

        for i in range(len(vetor)):
            X.append(vetor[i][0])
            Y.append(vetor[i][1])
            Z.append(vetor[i][2])
        ax.scatter(X, Y, Z, c='r', marker='o')
        ax.grid()
        plt.savefig(options.folder + '/' + title + '.png')
        plt.show()
