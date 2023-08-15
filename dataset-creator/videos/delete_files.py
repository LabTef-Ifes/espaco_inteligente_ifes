import os
import glob

# Get the current directory
current_dir = os.getcwd()
path = os.path.join(current_dir, "p001g01")
#Apaga as imagens que terminam com valores menores que 80
for filename in glob.glob(os.path.join(path, '*.jpeg')):
    os.remove(filename)