import shutil
import json


source_file = '0.json'
with open(source_file) as f:
    config = json.load(f)
    # print(config)

fps = config['initial_config']['sampling']['frequency']
novo_fps = input("Insira o novo valor de  ou enter para manter:") or fps

while True:
    try:
        novo_fps = float(novo_fps)
    except:
        print("Entrada inválida, insira um número inteiro válido")
        novo_fps = input("Insira o novo valor de  ou enter para manter:") or fps

    else:
        break


config['initial_config']['sampling']['frequency'] = novo_fps

with open(source_file, 'w+') as f:
    json.dump(config, f, indent=2)
for c in range(1, 4):
    shutil.copyfile(source_file, str(c)+'.json')


#Incompleto
# Atualiza o options.json na outra pasta
options_path = '..\\dataset-creator\\options.json'

with open(options_path) as f:
    options = json.load(f)
    print(options)
