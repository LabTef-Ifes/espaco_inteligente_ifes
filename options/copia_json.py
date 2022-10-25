import shutil
import json


def valid(default, var):
    """valida uma variável int

    Args:
        default (Any): Valor padrão caso o usuário deseje pular essa alteração
    """
    novo = input(
        f"Insira o novo valor de {var} ou enter para manter:") or default

    while True:
        try:
            novo = int(novo)
        except:
            print("Entrada inválida, insira um número inteiro válido")
            novo = input(
                f"Insira o novo valor de {var} ou enter para manter:") or default

        else:
            return novo


source_file = '0.json'

with open(source_file) as f:
    config = json.load(f)
    # print(config)

fps = config['initial_config']['sampling']['frequency']
novo_fps = valid(fps, 'fps')
width = valid(config['initial_config']['image']
              ['resolution']['width'], 'width')
height = valid(config['initial_config']['image']
               ['resolution']['height'], 'height')


config['initial_config']['sampling']['frequency'] = novo_fps
config['initial_config']['image']['resolution']['height'] = height
config['initial_config']['image']['resolution']['width'] = width

# Copia o novo fps para os jsons 1-3
for c in range(1, 4):
    with open(str(c)+source_file[1:], 'w+') as f:
        config['camera_id'] = c
        json.dump(config, f, indent=2)
     
# Atualiza o options.json na outra pasta
options_path = '../dataset-creator/options.json'
with open(options_path) as f:
    options = json.load(f)
    for i, cam in enumerate(options["cameras"]):
        options["cameras"][i]['config']["sampling"]['frequency'] = novo_fps
        options["cameras"][i]['config']['image']['resolution']['width'] = width
        options["cameras"][i]['config']['image']['resolution']['height'] = height
    print(novo_fps, width, height)

with open(options_path, 'w+') as f:
    json.dump(options, f, indent=2)
