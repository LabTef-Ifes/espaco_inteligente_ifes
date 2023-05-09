import shutil
import json

# Path para o arquivo options.json
options_path = 'dataset-creator/options.json'

# Path para o arquivo options.json
options_path = 'dataset-creator/options.json'


def valid(default, var) -> int:
    """valida uma variável int

    Args:
        default (int): Valor padrão caso o usuário deseje pular essa alteração
        var (str): Nome da variável para o input
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


def user_input():
    with open('options/0.json') as f:
        config = json.load(f)

    old_fps = config['initial_config']['sampling']['frequency']

    novo_fps = valid(old_fps, 'fps')
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

    return novo_fps, width, height, color


def atualiza_json(path, novo_fps, width, height, color):
    with open(path) as f:
        config = json.load(f)

    # Atualiza o dicionario
    config['initial_config']['sampling']['frequency'] = novo_fps
    config['initial_config']['image']['resolution']['width'] = width
    config['initial_config']['image']['resolution']['height'] = height
    config['initial_config']['image']['color_space']['value'] = color

    # Sobreescreve os valores atualizados
    with open(path, 'w+') as f:
    return novo_fps, width, height, color


def atualiza_json(path, novo_fps, width, height, color):
    with open(path) as f:
        config = json.load(f)

    # Atualiza o dicionario
    config['initial_config']['sampling']['frequency'] = novo_fps
    config['initial_config']['image']['resolution']['width'] = width
    config['initial_config']['image']['resolution']['height'] = height
    config['initial_config']['image']['color_space']['value'] = color

    # Sobreescreve os valores atualizados
    with open(path, 'w+') as f:
        json.dump(config, f, indent=2)


if __name__ == '__main__':

    novo_fps, width, height, color = user_input()

    for c in range(0, 4):
        path = f'options/{c}.json'
        atualiza_json(path, novo_fps, width, height, color)

    # Atualiza o options.json na outra pasta
    with open(options_path) as f:
        options = json.load(f)
    for i, _ in enumerate(options["cameras"]):
        options["cameras"][i]['config']["sampling"]['frequency'] = novo_fps
        options["cameras"][i]['config']['image']['resolution']['width'] = width
        options["cameras"][i]['config']['image']['resolution']['height'] = height
        options["cameras"][i]['config']['image']['color_space']['value'] = color
    with open(options_path, 'w+') as f:
        json.dump(options, f, indent=2)

    print(novo_fps, width, height, color)
