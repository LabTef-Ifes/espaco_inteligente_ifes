'''Execute esse script caso obtenha o erro
"sh: 1: ./...sh: Permission denied"

Exemplos:
sh: 1: ./sh_files/is-cameras.sh: Permission denied
sh: 1: ./sh_files/is-skeletons-detector.sh: Permission denied
sh: 1: ./sh_files/is-frame-transformation.sh: Permission denied
sh: 1: ./sh_files/is-skeletons-grouper.sh: Permission denied

'''

import os
os.system("chmod +x sh_files/*.sh")

