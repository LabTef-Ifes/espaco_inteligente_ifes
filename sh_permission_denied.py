'''Execute esse script caso obtenha o erro

sh: 1: ./is-basic.sh: Permission denied
sh: 1: ./is-cameras.sh: Permission denied
sh: 1: ./is-skeletons-detector.sh: Permission denied
sh: 1: ./is-frame-transformation.sh: Permission denied
sh: 1: ./is-skeletons-grouper.sh: Permission denied
'''

import os
os.system("chmod +x is-basic.sh")
os.system("chmod +x is-cameras.sh")
os.system("chmod +x is-skeletons-detector.sh")
os.system("chmod +x is-frame-transformation.sh")
os.system("chmod +x is-skeletons-grouper.sh")
