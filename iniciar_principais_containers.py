# -*- coding: utf-8 -*-

import os
import time
#os.system('sudo docker container stop $(sudo docker container ls -q)') # Para todos os containeres que estejam rodando antes.
os.system("./sh_files/is-basic.sh")
time.sleep(15) # espera o primeiro iniciar pois dá um pico de memoria
os.system("./sh_files/is-cameras.sh")
os.system("./sh_files/is-skeletons-detector.sh")
os.system("./sh_files/is-frame-transformation.sh")
os.system("./sh_files/is-skeletons-grouper.sh")
