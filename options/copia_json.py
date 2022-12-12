import shutil
import json


def valid(default, var) -> int:
    """valida uma variável int

    Args:
        default (Any): Valor padrão caso o usuário deseje pular essa alteração
        var (Any): Nome da variável para o input
    Returns:
        novo (int)
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
# Path para o arquivo options.json
options_path = '../dataset-creator/options.json'


with open(source_file) as f:
    config = json.load(f)
    # print(config)

fps = config['initial_config']['sampling']['frequency']
novo_fps = valid(fps, 'fps')
width = valid(config['initial_config']['image']
              ['resolution']['width'], 'width')
height = valid(config['initial_config']['image']
               ['resolution']['height'], 'height')

color = input("Color(RGB ou GRAY):").upper(
) or config['initial_config']['image']['color_space']['value']
while color not in ('RGB', 'GRAY', ''):
    print("Erro, digite um valor válido")
    color = input("Color(RGB ou GRAY):").upper(
    ) or config['initial_config']['image']['color_space']['value']

# Atualiza o dicionario
config['initial_config']['sampling']['frequency'] = novo_fps
config['initial_config']['image']['resolution']['height'] = height
config['initial_config']['image']['resolution']['width'] = width
config['initial_config']['image']['color_space']['value'] = color
# Copia os novos valores para os jsons 0-3
for c in range(0, 4):
    with open(str(c)+source_file[1:], 'w+') as f:
        # Atualiza o id das câmeras para o valor correto
        config['camera_id'] = c
        json.dump(config, f, indent=2)

# Atualiza o options.json na outra pasta
with open(options_path) as f:
    options = json.load(f)  
for i, _ in enumerate(options["cameras"]):
    options["cameras"][i]['config']["sampling"]['frequency'] = novo_fps
    options["cameras"][i]['config']['image']['resolution']['width'] = width
    options["cameras"][i]['config']['image']['resolution']['height'] = height
    options["cameras"][i]['config']['image']['color_space']['value'] = color
print(novo_fps, width, height, color)
with open(options_path, 'w+') as f:
    json.dump(options, f, indent=2)
