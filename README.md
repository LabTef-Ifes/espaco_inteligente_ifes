![Reconstrução tridimensional](caminhada.gif)

# Summary

- [Summary](#summary)
- [Preparando o ambiente](#preparando-o-ambiente)
  - [Requisitos de instalação](#requisitos-de-instalação)
  - [Instale o ambiente](#instale-o-ambiente)
- [Câmeras antigas - Informações importantes](#câmeras-antigas---informações-importantes)
- [Comentários sobre o uso dos containers](#comentários-sobre-o-uso-dos-containers)
  - [Grouper](#grouper)
  - [Mjpeg](#mjpeg)
- [Pastas e arquivos do espaço inteligente](#pastas-e-arquivos-do-espaço-inteligente)
  - [root(pasta inicial do diretório)](#rootpasta-inicial-do-diretório)
  - [dataset-creator](#dataset-creator)
    - [calculate.py](#calculatepy)
      - [Classe Skeleton](#classe-skeleton)
        - [Joint](#joint)
      - [Classe Calculate](#classe-calculate)
        - [Vector](#vector)
        - [Atributos](#atributos)
        - [Funções](#funções)
        - [Velocidade](#velocidade)
        - [Alinhamento dos ombros](#alinhamento-dos-ombros)
        - [Distância](#distância)
        - [Alinhamento do tronco](#alinhamento-do-tronco)
        - [Ângulo dos joelhos](#ângulo-dos-joelhos)
        - [Altura do pé](#altura-do-pé)
        - [Ângulo entre os joelhos](#ângulo-entre-os-joelhos)
      - [Classe Plot](#classe-plot)
  - [sh\_files](#sh_files)
  - [is-camera-py-labtef](#is-camera-py-labtef)
  - [calibrations](#calibrations)
  - [options](#options)
- [Câmeras novas do switch e o novo serviço de gateway](#câmeras-novas-do-switch-e-o-novo-serviço-de-gateway)
  - [Como iniciar as câmeras](#como-iniciar-as-câmeras)
- [Configurações do Labtef - PC 20](#configurações-do-labtef---pc-20)
- [Referências](#referências)
  - [Papers](#papers)
  - [Repositório do gateway das novas câmeras](#repositório-do-gateway-das-novas-câmeras)
  - [Pasta de artigos](#pasta-de-artigos)
  - [Espaço Inteligente](#espaço-inteligente)
  - [Calibração das câmeras](#calibração-das-câmeras)
  - [Skeleton Detector](#skeleton-detector)
- [Recomendações de estudo](#recomendações-de-estudo)
- [Reiniciando o PC 20 do Labtef](#reiniciando-o-pc-20-do-labtef)

---

# Preparando o ambiente
Em dezembro de 2023, estamos atualizando uma nova máquina utilizando o EI com Ubuntu 22.04.

## Requisitos de instalação
- [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04)
- [Docker Compose](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04)
- [Nvidia Docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/1.14.3/install-guide.html#installing-with-apt)
- [Python 3.10.10](https://www.linuxcapable.com/how-to-install-python-3-10-on-ubuntu-linux/)
- [Nvidia Drivers](https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/index.html)

## Instale o ambiente

**Para utilizar o GitHub no Linux, é recomendado utilizar a extensão github nativa no VsCode**

1. Adicione o seu usuario para utilizar o docker sem sudo com `sudo usermod -aG docker $USER`.
2. Crie uma pasta local para o projeto com o nome `desenvolvimento`
    <ol type="i">
    <li>Para sincronizar esse repositório à uma pasta local na sua máquina Linux, abra o terminal e digite <code>git clone https://github.com/LabTef-Ifes/espaco_inteligente_ifes</code> para o repositório principal ou <code>git clone https://github.com/LabTef-Ifes/espaco_inteligente_ifes-deivid</code> para <i>clonar</i> o fork de atualização.
    <li>Crie um <i>virtual environment</i> para o projeto <br> Para criar um venv, digite <code>python3.10 -m venv venv</code> no diretório reservado ao projeto.
    <li>Ative o ambiente virtual com o comando <code>source venv/bin/activate</code>.
    </ol>
3. Dentro da pasta clonada, clone o repositório [is-camera-py-labtef](https://github.com/LabTef-Ifes/is-cameras-py-labtef) com o comando `git clone https://github.com/LabTef-Ifes/is-cameras-py-labtef`
4. Com o `venv` ativo, instale as bibliotecas necessárias para o espaço inteligente (EI) escritas no arquivo [requirements.txt](requirements.txt) através do comando `pip install -r requirements.txt`.
5. Execute os containers necessários para o funcionamento do EI: execute o arquivo [iniciar_principais_containers.sh](iniciar_principais_containers.sh) com $`sh iniciar_principais_containers.sh`.
   1. Caso se depare com o erro de **permission denied**, execute o arquivo [sh_permission_denied.py](sh_permission_denied.py) e execute o arquivo [iniciar_principais_containers.sh](iniciar_principais_containers.sh) novamente.
6. Em outro terminal, digite `docker stats` para verificar se os containers estão rodando (_Ctrl+C para fechar_). Os containers em funcionamento do EI são (verificar o parâmetro _NAME_ no terminal):

   | containers ativos (**Comunicação**) |                                 **descrição** |
   | :---------------------------------- | --------------------------------------------: |
   | rabbitmq                            |              Canal de comunicação dos tópicos |
   | zipkin                              | Exibe e organiza os tópicos para visualização |

   | **Câmeras antigas**[^1] |   **descrição** |
   | :---------------------- | --------------: |
   | cam0                    | Conexão da cam0 |
   | cam1                    | Conexão da cam1 |
   | cam2                    | Conexão da cam2 |
   | cam3                    | Conexão da cam3 |

   | **Reconstrução**        |                                                                                             **descrição** |
   | :---------------------- | --------------------------------------------------------------------------------------------------------: |
   | skX [^3]                | Serviço de transformação dos esqueletos 2d em esqueletos 3d. Utilizado no arquivo `request_3d.py` |
   | is-frame_transformation |                                            Serviço de transformar esqueletos 2d em 3d usando a calibração |
   | grouper                 |                                                                           Descrito na [citação](#grouper) |

---

# Câmeras antigas - Informações importantes

- Para alterar os parâmetros de `fps`, `width`, `height` e `color` das câmeras, utlize o [options/copia_json.py](options/copia_json.py)
- O arquivo `capture_images.py` só irá mostrar as imagens das 4 câmeras com todas elas funcionando. Caso uma ou mais câmeras não estejam funcionando, o programa não irá mostrar as imagens.
- A câmera _antiga_[^1] possui uma limitação quanto ao número de frames por segundo de acordo com seu modo de cor.
  1. Na opção **RGB** (_pixel format RGB8_) as câmeras funcionam com até **12 fps** (1288 width, 728 heigth).
  2. Na opção **GRAY** (_pixel format Mono8_) as câmeras irão funcionar com até **30 fps** (1288 width, 728 heigth).
  3. Informações adicionais podem ser encontradas nas [referências técnicas](./referencias-tecnicas) das câmeras.
- As alterações realizadas nos arquivos `options/X.json`[^3] somente surtirão efeito ao (_re_)inicializar os containers.
  ⚠️ _Caso os containers estejam ativos e for realizada alguma mudançaa nos arquivos json, os containers deverão ser parados e reinicializados._
- Para parar todos os containers de uma só vez utilize o comando: `sudo docker container stop $(sudo docker container ls -q)`
- O Flycapture SDK, software do fabricante das câmeras, é compatível com o modelo _antigo_[^1].

- ⚠️⚠️O arquivo [options.json](dataset-creator/options.json) está vinculado às câmeras antigas e à captura de imagem, portando ele permanece sendo necessário de atualizar quando mudar parâmetros das câmeras.

[^3]: X representa o número da câmera entre 0 e a quantidade de câmeras. Com 4 câmeras, X pode ser 0,1,2 ou 3

# Comentários sobre o uso dos containers

_Seção criada a partir da primeira conversa com o Mendonça em busca de compreender a comunicação dockerizada do EI_

- O sistema de containeres foi criado pelo Felippe na Ufes e utilizado em seu mestrado.
- Há diversos tópicos de comunicação relacionados à captura de imagem, envio de imagem e construção do esqueleto.
- O `rabbit` e o `zipkin` são essenciais para a utilização da comunicação do EI e devem ser os primeiros serviços iniciados
- A ultima versão desenvolvida na Ufes da Image `frame-transformation` é a `0.0.4`
- Para calibrar as cameras, é necessario adicionar os arquivos `.json` com o _schema_ correto no diretorio definido no volume do docker `is-frame_transformation`

[^1]: modelo antigo **Blackfly GigE BFLY-PGE-09S2C**

## Grouper

<blockquote class="quote">
  <p>O serviço <a href='https://github.com/labviros/is-skeletons-grouper'>grouper</a>, quando operado no mode Stream, consome localizações de esqueleto feitas pelo serviço <a href='https://github.com/labviros/is-skeletons-detector'>is-skeletons-detector</a> por meio do tópico <code>SkeletonsDetector.(ID).Detection</code>, agrupa as localizações 2D dos esqueletos dentro de uma janela de tempo <i>a cada 100ms por exemplo</i>, faz a reconstrução 3D e publica em outro tópico <code>SkeletonsGrouper.(GROUP_ID).Localization</code> a localização. Ele também pode operar no modo <b>RPC</b>, em que você envia um grupo de esqueletos 2D, e ele retorna as localizações 3D. Esse serviço depende do serviço de <a href='https://github.com/labviros/is-frame-transformation'>Frame Transformation</a>, e este serviço precisa da pasta com as calibrações para inicializar.</p>
  <p>
      <footer>
      <cite>- Felippe Mendonça</cite>,
      <time datetime="2023-05-22">22 de maio de 2023</time>
      </footer>
  </p>
</blockquote>

## Mjpeg

<blockquote class="quote">
    <p>
        Mjpeg é um servidor de visualização de imagens do espaço inteligente. O repositório do projeto é este <a href=" https://github.com/labviros/is-mjpeg-server">aqui</a>.
        Por padrão ele exibe imagens de tópicos gerados por gateway de câmeras, que publicam os frames em <code>CameraGateway.${id}.Frame</code>. Para acessar uma câmera com ID diferente de zero, basta adicionar o <code>$id</code> no path da URL: http://localhost:3000/1, por exemplo.
    </p>
    <p>        
        <footer>
        <cite>- Felippe Mendonça</cite>,
        <time datetime="2023-06-05">05 de junho de 2023</time>
        </footer>
    </p>
</blockquote>

# Pastas e arquivos do espaço inteligente

## root(pasta inicial do diretório)

- [iniciar_principais_containers.sh](iniciar_principais_containers.sh) - Bash para iniciar todos os containers do EI em um computador conectados às câmeras[^2]
- [visualizar_camera.py](visualizar_camera.py) - Arquivo teste para visualizar a imagem de uma câmera.
- [sh_permission_denied.py](sh_permission_denied.py) - Desbloqueia os arquivos `.sh` em `sh_files` para execução
- [requirements.txt](requirements.txt) - Lista todas as bibliotecas necessárias para o funcionamento do EI. É utilizado para fazer a instalação de todas as bibliotecas do ambiente, como descrito na [preparação do ambiente](#preparando-o-ambiente)

## dataset-creator

- [dataset-creator/capture_images.py](dataset-creator/capture_images.py) - Realiza a captura dos frames das 4 câmeras e os salva no diretório especificado em `./dataset-creator/options.json`. Comandos válidos: `s` inicia a gravação (salvar imagens), `p` pausa a gravação, `q` fecha o programa.

- [dataset-creator/make_videos.py](/dataset-creator/make_videos.py) - A partir dos frames capturados pelo arquivo `capture_images.py`, monta os vídeos de cada câmera e os salva em formato `.mp4`.
- [dataset-creator/request_2d.py](dataset-creator/request_2d.py) - Utiliza o openpose para detectar os esqueletos em imagens de cada câmera, isoladamente. O processo é realizado através de comunicação com Dockers desenvolvidos pelos laboratórios da UFES.
- [dataset-creator/request_3d.py](dataset-creator/request_3d.py) - Utiliza os jsons gerados pelo `request_2d.py` e cruza os esqueletos em função do tempo, obtendo os dados 3d do esqueleto. O processo é realizado através de comunicação com Dockers desenvolvidos pelos laboratórios da UFES.
- [dataset-creator/options.json](dataset-creator/options.json) - Parâmetros da criação gravação e análise dos vídeos. Neste arquivo, é possível alterar o diretório onde os frames das câmeras serão salvos para posteriormente formarem vídeos.
- [dataset-creator/export-video-3d-medicoes-e-erros.py](dataset-creator/export-video-3d-medicoes-e-erros.py) - Arquivo do Wyctor utilizado para realizar cálculos sobre a reconstrução 3D **Deprecated**
- [dataset-creator/Parameters.py](dataset-creator/Parameters.py) - programa que possui funções usadas no arquivo `export-video-3d-medicoes-e-erros.py`. **Deprecated**

### [calculate.py](dataset-creator/calculate.py)

A partir do arquivo json gerado pelo `request_3d.py`, calcula as métricas e os gráficos da gravação

#### Classe Skeleton

Representa um esqueleto humano. Possui os seguintes métodos e atributos:

`__init__(self, frame_dict: dict)`
Construtor da classe que recebe um dicionário frame_dict contendo informações sobre os keypoints do esqueleto. Este dicionário é extraído de um frame de um vídeo. Os principais atributos são:

`objects`: Uma lista de dicionários, onde cada dicionário representa um objeto (pessoa) no frame.

`keypoints`: Uma lista de dicionários contendo as coordenadas tridimensionais dos keypoints de cada pessoa no frame.

`joints`: Um dicionário que mapeia os IDs dos keypoints para objetos da classe Joint.

`read_joints(self) -> dict[str, Skeleton.Joint]`
Este método lê os keypoints do esqueleto a partir dos dados do frame e retorna um dicionário com os keypoints representados como objetos da classe Joint.

##### Joint

Possui os pontos `x`,`y`,`z` de um dado ponto do corpo.
Possui `id` e `nome`
Pode fazer divisão por um número.
Pode somar com outra `Joint`.

#### Classe Calculate
Realiza todos os cálculos de movimento e posição utilizando a classe Skeleton.
##### Vector

Classe interna dentro da classe `Calculate` que representa um vetor tridimensional. Essa classe é usada para calcular a magnitude e o ângulo entre dois vetores, que são frequentemente utilizados no contexto do processamento de keypoints tridimensionais do esqueleto humano.

Método `init(self, point_a, point_b)`
O construtor da classe `Calculate.Vector` recebe dois objetos do tipo `Skeleton.Joint`, que representam pontos no espaço tridimensional. Ele cria um vetor cuja origem está no ponto `point_a` e cujo destino está no ponto `point_b`. O vetor é definido pelas coordenadas (x, y, z) do ponto de origem e do ponto de destino.

Propriedade `vector`
A propriedade `vector` retorna uma representação do vetor como um array NumPy, contendo as componentes x, y e z do vetor.

Propriedade `magnitude`
A propriedade `magnitude` calcula a magnitude (comprimento) do vetor usando a função `np.linalg.norm` da biblioteca NumPy. A magnitude é uma medida do tamanho do vetor no espaço tridimensional.

Método `calculate_angle(self, vector)`
O método `calculate_angle` calcula o ângulo entre dois vetores. Ele recebe outro objeto do tipo `Calculate.Vector` como argumento e calcula o ângulo entre o vetor atual (representado pela instância `self`) e o vetor passado como argumento usando o produto interno (dot product) entre os dois vetores. O resultado é retornado em graus.

Operador `floordiv(self, other)`
O operador `floordiv` é definido para calcular o ângulo entre dois vetores usando a função `calculate_angle`. Quando você usa o operador `//` entre duas instâncias da classe `Calculate.Vector`, ele chama o método `calculate_angle` para calcular o ângulo entre esses vetores.

A classe `Calculate.Vector` é útil para calcular ângulos e magnitudes entre pontos tridimensionais, o que é fundamental para várias métricas e cálculos realizados na classe `Calculate` ao processar os keypoints do esqueleto humano.

##### Atributos
`human_parts_id`: Um dicionário que mapeia os IDs dos keypoints para seus nomes correspondentes.

`human_parts_name`: Um dicionário que mapeia os nomes dos keypoints para seus IDs correspondentes.

`file3d`: O nome do arquivo JSON contendo os dados.

`plot_data`: Um dicionário usado para armazenar os resultados dos cálculos que serão usados para a geração de gráficos.

`data`: Uma lista de frames, onde cada frame contém informações sobre os keypoints do esqueleto.

`frames`: O número total de frames no arquivo.

`skeleton`: Um objeto da classe `Skeleton` que representa o esqueleto no primeiro frame.

`dt`: O tempo entre cada frame (inverso da taxa de quadros por segundo).

`midpoint_history`: Uma lista para armazenar os pontos médios entre as duas `hips` (quadril) para calcular a velocidade.

##### Funções
`__init__(self, file3d)`
Construtor da classe que recebe o nome de um arquivo JSON contendo os dados tridimensionais dos keypoints do esqueleto. Os principais atributos são:

`run_frames(self)`
Este método passa por todos os frames do arquivo JSON e realiza vários cálculos, incluindo velocidade, distância entre os pés, altura dos ombros, altura dos pés, ângulo do tronco e ângulos dos joelhos. Os resultados são armazenados no dicionário `plot_data`.


##### Velocidade

`velocidade(self)`: Calcula a velocidade com base no deslocamento do ponto médio entre as duas `hips`.

##### Alinhamento dos ombros

`alinhamento_ombros(self)`: Calcula a altura dos ombros esquerdo e direito.

##### Distância

`distancia_pes(self)`: Calcula a distância entre os pés.

##### Alinhamento do tronco

`angulo_tronco_vertical(self)`: Calcula o ângulo do tronco em relação ao eixo vertical.

##### Ângulo dos joelhos

`angulo_joelho_direito(self)`: Calcula o ângulo do joelho direito.

`angulo_joelho_esquerdo(self)`: Calcula o ângulo do joelho esquerdo.

##### Altura do pé

`altura_do_pe(self, lado)`: Calcula a altura do tornozelo (esquerdo ou direito).

##### Ângulo entre os joelhos

`angulo_pelvis(self)`: Calcula o ângulo da pelvis.

#### Classe Plot

A classe `Plot` é responsável por criar gráficos a partir dos dados calculados pela classe `Calculate`. Ela possui os seguintes métodos:

`__init__(self, data)`
Construtor da classe que recebe o dicionário `data` contendo os resultados dos cálculos da classe `Calculate`.

`plot(self)`
Este método chama vários outros métodos para criar gráficos de diferentes métricas, como altura dos ombros, ângulos dos joelhos, distância entre os pés, entre outros. Os gráficos são salvos na pasta `resultados`.

Os gráficos gerados incluem:

1. Altura dos ombros
2.  Ângulos dos joelhos
3. Ângulo do tronco
4. Altura dos pés (tornozelos)
5. Distância entre os pés
6. Ângulo da pelvis

## sh_files

Pasta que contém todos os `bash` para executar os comandos `docker run` necessários para o EI

## is-camera-py-labtef

sub-repositório. [Mais informações](https://github.com/LabTef-Ifes/is-cameras-py-labtef)

## calibrations

Possui os jsons de calibração do ambiente. Esses jsons são utilizados para o docker `is-frame_transformation`. Atualmente, utiliza-se apenas os jsons dentro da pasta Ifes, pois foi a configuração que era utilizada pelo _docker run_ recebido.

## options

- [options/X.json](options/0.json)[^3]. Neste arquivo é possível alterar parâmetros relativos a câmera: `IP`, `fps`, `height`, `width` e etc.

# Câmeras novas do switch e o novo serviço de gateway

**❗Há problemas de conflito ao se utilizar o Spinnaker enquanto os containers das câmeras estão ativos.**

As câmeras _novas_[^2] adquiridas recentemente para o EI não funcionam com o serviço de gateway já disponível. Desta forma, [um novo serviço de gateway](https://github.com/LabTef-Ifes/is-cameras-py) foi desenvolvido. Em sua primeira utilização, execute as instruções contidas no Readme e conseguirá visualizar a imagem de uma câmera.

Para iniciar as quatro câmeras de uma só vez, execute o comando `sudo docker compose up` dentro da pasta `deploy/multi-camera`. As configurações das câmeras podem ser alterados nos arquivos `settings-camera-X.yaml`[^3] também contidos na pasta `deploy/multi-camera`.  Os parâmetros disponíveis para alteração são `fps`, `formato de cores`, `height`, `width` e `ratio`.
❗ Caso não exista o arquivo correspondente a cada uma das câmeras, crie os demais.

Com os containers ativos, os arquivo do EI podem ser utilizados normalmente. Os containers que estarão ativos serão (_Name_):

| Containers(_Name_)             |                       descrição |
| :----------------------------- | ------------------------------: |
| multi-camera-rabbitmq-1        |            Comunicação RabbitMQ |
| multi-camera-is-mjpeg-server-1 | [Descrição do Mendonça](#mjpeg) |
| multi-camera-camera-X-1        |         Conexão da câmera X[^3] |

- O Readme contido dentro do arquivo `spinnaker-2.7.0.128-Ubuntu18.04-amd64-pkg.tar.gz` possui informações -_sobre alteração de buffer, por exemplo_- que podem ajudar caso esteja ocorrendo algum problema de captura de imagem.
- O `Spinnaker SDK` é o software do fabricante das câmeras compatível com o modelo _novo_[^2] e com o modelo _antigo_[^1]
<!-- Aqui está Spinnaker SDK e mais acima está Flycapture SDK. Qual é o certo? -->

[^2]: modelo novo **Blackfly S GigE BFS-PGE-16S2C-CS**

## Como iniciar as câmeras

1. Conecte a câmera no Switch físico
2. Abra o software **SpinView**
3. Clique com o botão direito no IP da câmera e clique em `Auto Force IP`
4. Confira que os IP's das câmeras estão corretos nos arquivos `settings-camera-X.yaml`[^3], dentro de [multi-camera](is-cameras-py-labtef\deploy\multi-camera)
5. Inicie os containers com o comando `sh iniciar_principais_containers.sh` na pasta principal.
6. Confira que os containeres listados estão em execução
7. Inicie o seu ambiente virtual
8. As câmeras foram iniciadas, visualize-as com o script `visualizar_camera.py`, executado dentro do ambiente virtual.

# Configurações do Labtef - PC 20

| Item                   |                                                                                    Detalhamento |
| :--------------------- | ----------------------------------------------------------------------------------------------: |
| S.O                    |                                                                              Ubuntu 18.04.5 LTS |
| Processador            |                                                          Intel® Core™ i5-8400 CPU @ 2.80GHz × 6 |
| RAM                    |                                                                                            16GB |
| Placa de vídeo         |                                                               NVIDIA GeForce GTX 1070/PCIe/SSE2 |
| Placa de rede          |                                                                                fibra ótica 10Gb |
| Versão do Python       |                                                                                           3.6.9 |
| Switch                 |                                                                   3Com Switch 4800G PWR 24-Port |
| Portas com PoE ativado |                                                                             19, 21, 22, 23 e 24 |
| Charuco                | detalhado no [repositório de calibração](https://github.com/LabTef-Ifes/camera-calibration-new) |
# Referências

## Papers

- [Tese de Doutorado - Rampinelli, Mariana (2014)](papers/Tese%20Doutorado%20Calibracao%20Câmeras%20Robo%20Mariana%20Rampinelli.pdf)
- [Relatório Final de IC - Smarzaro, Deivid (2023)](papers/Relatório%20Final%202023.pdf)

## Repositório do gateway das novas câmeras

- [Spinnaker Gateway do Felippe Mendonça](https://github.com/LabTef-Ifes/is-cameras-py)
- [Spinnaker Gateway modificado para o LabTeF](https://github.com/LabTef-Ifes/is-cameras-py-labtef)

## Pasta de artigos

- [Drive da Mariana](https://drive.google.com/drive/folders/1TIPGF9pkX-jDV5Voz08XtdeS18ijzYBG?usp=sharing)
- [PPSUS 2021](https://drive.google.com/drive/folders/1USJJMGo9zSRY3Z4sJmGX9pXoy-Q5_ksf?usp=sharing)

## Espaço Inteligente

- Projeto original: [LabViros](https://github.com/labviros)
- [Curso de Espaço Inteligente](https://github.com/LabTef-Ifes/CursoEI)
- [Repositório do Wyctor](https://github.com/wyctorfogos/ESPACOINTELIGENTE-IFES)
- [dataset-creator original](https://github.com/felippe-mendonca/dataset-creator/)
- LabVISIO - Laboratório de Visão Computacional, Robótica e Espaços Inteligentes (UFES): [GitHub](https://github.com/labvisio) / [Site](https://visio.ufes.br/)

## Calibração das câmeras

- [is-aruco-camera-calibration](https://github.com/LabTef-Ifes/is-aruco-camera-calibration) _Referência_
- [Camera Calibration New](https://github.com/LabTef-Ifes/camera-calibration-new) **Working**
- [Camera Calibration](https://github.com/LabTef-Ifes/camera-calibration) **Deprecated**

## Skeleton Detector

- [Skeleton Detector do Felippe Mendonça](https://github.com/labviros/is-skeletons-detector)

---

# Recomendações de estudo

- [Introdução aos conceitos do EI - CursoEI](https://github.com/LabTef-Ifes/CursoEI)
- [Github by The Coding Train](https://www.youtube.com/playlist?list=PLRqwX-V7Uu6ZF9C0YMKuns9sLDzK6zoiV)
- [Curso de Git e GitHub do CursoEmVideo](https://www.cursoemvideo.com/curso/curso-de-git-e-github/)
- [Virtual Environment](https://docs.python.org/3/library/venv.html)
---

# Reiniciando o PC 20 do Labtef

Em caso de crash do pc, é necessário reiniciá-lo pelo botão físico e seguir os passos abaixo .

1. Selecione Ubuntu no menu de fundo roxo
2. digite `fsck /dev/sda1` na tela preta de terminal _⚠️atenção ao espaço_
3. aperte `y` para aceitar cada alteração
4. digite `reboot`
