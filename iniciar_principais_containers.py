# -*- coding: utf-8 -*-
import os
import time
os.system('sudo docker container stop $(sudo docker container ls -q)') # Para todos os containeres que estejam rodando antes.
os.system('sudo python sh_permission_denied.py')
#os.system('cd is-cameras-py-labtef/deploy/multi-camera && sudo docker compose up -d')
#os.system("./sh_files/is-basic.sh")
#os.system("./sh_files/is-cameras.sh")
#time.sleep(5)
os.system("./sh_files/is-rabbitmq.sh")
os.system("./sh_files/is-zipkin.sh")
os.system("./sh_files/is-mjpeg.sh")
#os.system("./sh_files/is-skeletons-detector.sh")
os.system("./sh_files/is-frame-transformation.sh")
os.system("./sh_files/is-skeletons-grouper.sh")
