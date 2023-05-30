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

# Classe sem self??? Acredito que eram todos staticmethod's, porém não declarados corretamente
class Plot:
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

        #  Má utilização de subplot
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

        fig, ax = plt.subplots()
        ax.plot(y)
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
        sigma_new_vec = desvio_padrao_curva_media  # ynew-aux
        lower_bound = y - sigma_new_vec
        upper_bound = y + sigma_new_vec

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
