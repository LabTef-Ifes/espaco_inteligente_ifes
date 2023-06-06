'''Execute esse script caso obtenha o erro

sh: 1: ./sh_files/is-basic.sh: Permission denied
sh: 1: ./sh_files/is-cameras.sh: Permission denied
sh: 1: ./sh_files/is-skeletons-detector.sh: Permission denied
sh: 1: ./sh_files/is-frame-transformation.sh: Permission denied
sh: 1: ./sh_files/is-skeletons-grouper.sh: Permission denied

'''

import os
os.system("chmod +x ./sh_files/is-rabbitmq.sh")
os.system("chmod +x ./sh_files/is-zipkin.sh")
os.system("chmod +x ./sh_files/is-mjpeg.sh")
os.system("chmod +x ./sh_files/is-cameras.sh")
os.system("chmod +x ./sh_files/is-skeletons-detector.sh")
os.system("chmod +x ./sh_files/is-frame-transformation.sh")
os.system("chmod +x ./sh_files/is-skeletons-grouper.sh")
