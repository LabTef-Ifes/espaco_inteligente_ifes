# -*- coding: utf-8 -*-
import os
import time
# Iniciar sem cameras conectadas. Ativa as comunicações e as reconstruções. Necessário ter a calibração
os.system('sudo docker rm -f $(sudo docker container ls -q)') # Para todos os containeres que estejam rodando antes.
os.system('sudo python sh_permission_denied.py')
time.sleep(1)
os.system("./sh_files/is-rabbitmq.sh")
time.sleep(1)
os.system("./sh_files/is-zipkin.sh")
time.sleep(1)
os.system("./sh_files/is-mjpeg.sh")
time.sleep(1)
os.system("./sh_files/is-skeletons-detector.sh")
time.sleep(1)
os.system("./sh_files/is-frame-transformation.sh")
time.sleep(1)
os.system("./sh_files/is-skeletons-grouper.sh")
