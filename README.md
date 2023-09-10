![Reconstrução tridimensional](caminhada.gif)

# Summary
- [Summary](#summary)
- [Preparando o ambiente](#preparando-o-ambiente)
  - [Instale o Docker](#instale-o-docker)
- [Câmeras antigas - Informações importantes](#câmeras-antigas---informações-importantes)
- [Comentários sobre o uso dos containers](#comentários-sobre-o-uso-dos-containers)
  - [Grouper](#grouper)
- [Pastas e arquivos do espaço inteligente](#pastas-e-arquivos-do-espaço-inteligente)
  - [root(pasta inicial do diretório)](#rootpasta-inicial-do-diretório)
  - [dataset-creator](#dataset-creator)
    - [calculate.py](#calculatepy)
      - [Classe Skeleton](#classe-skeleton)
      - [Classe Calculate](#classe-calculate)
        - [Ângulo dos joelhos](#ângulo-dos-joelhos)
        - [Alinhamento do tronco](#alinhamento-do-tronco)
        - [Velocidade](#velocidade)
        - [Distância](#distância)
      - [Classe Calculate.Vector](#classe-calculatevector)
      - [Classe Plot](#classe-plot)
      - [Altura do pé](#altura-do-pé)
  - [sh\_files](#sh_files)
  - [is-camera-py-labtef](#is-camera-py-labtef)
  - [calibrations](#calibrations)
  - [options](#options)
- [Câmeras novas do switch e o novo serviço de gateway](#câmeras-novas-do-switch-e-o-novo-serviço-de-gateway)
  - [Como iniciar as câmeras](#como-iniciar-as-câmeras)
- [Configurações do Labtef](#configurações-do-labtef)
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

**Para utilizar o GitHub no Linux, é recomendado utilizar a extensão github nativa no VsCode**
1. Adicione o seu usuario para utilizar o docker sem sudo com `sudo usermod -aG docker $USER`.
2. Crie uma pasta local para o projeto com o nome `desenvolvimento`
	<ol type="i">
	<li>Para sincronizar esse repositório à uma pasta local na sua máquina Linux, abra o terminal e digite <code>git clone https://github.com/LabTef-Ifes/espaco_inteligente_ifes</code> para o repositório principal ou <code>git clone https://github.com/LabTef-Ifes/espaco_inteligente_ifes-deivid</code> para <i>clonar</i> o fork de atualização.
	<li>
	    Crie um <i>virtual environment</i> para o projeto
		    Para criar um venv, digite <code>python3.6 -m venv venv</code> no diretório reservado ao projeto.
	<li>Ative o ambiente virtual com o comando <code>source venv/bin/activate</code>.
	</ol>
3. Dentro da pasta clonada, clone o repositório [is-camera-py-labtef](https://github.com/LabTef-Ifes/is-cameras-py-labtef) com o comando `git clone https://github.com/LabTef-Ifes/is-cameras-py-labtef` 
4. Com o `venv` ativo, instale as bibliotecas necessárias para o espaço inteligente (EI) escritas no arquivo [requirements.txt](requirements.txt) através do comando `pip install -r requirements.txt`.
5. Execute os containers necessários para o funcionamento do EI: execute o arquivo [iniciar_principais_containers.sh](iniciar_principais_containers.sh). 
   1. Caso se depare com o erro de **permission denied**, execute o arquivo [sh_permission_denied.py](sh_permission_denied.py) e execute o arquivo [iniciar_principais_containers.sh](iniciar_principais_containers.sh) novamente.
   
6. Em outro terminal, digite `sudo docker stats` para verificar se os containers estão rodando (*Ctrl+C para fechar*). Os containers em funcionamento do EI são (verificar o parâmetro _NAME_ no terminal):
   

    | containers ativos (**Comunicação**) |                                                                                             **descrição** |
    | :---------------------------------- | --------------------------------------------------------------------------------------------------------: |
    | rabbitmq                            |                                                                          Canal de comunicação dos tópicos |
    | zipkin                              |                                                             Exibe e organiza os tópicos para visualização |
    | **Câmeras antigas[^1]**             |                                                                                             **descrição** |
    | cam0                                |                                                                                           Conexão da cam0 |
    | cam1                                |                                                                                           Conexão da cam1 |
    | cam2                                |                                                                                           Conexão da cam2 |
    | cam3                                |                                                                                           Conexão da cam3 |
    | **Reconstrução**                    |                                                                                             **descrição** |
    | skX (X in [1,2,...])                | Serviço de transformação dos esqueletos 2d em esqueletos 3d. Utilizado no arquivo request-3d-skeletons.py |
    | is-frame_transformation             |                                            Serviço de transformar esqueletos 2d em 3d usando a calibração |
    | grouper                             |                                                                    Descrito na [citação abaixo](#grouper) |

<!-- Comentado pois não é mais necessário ajustar essa pasta, pois está em relative path na pasta videos, dentro de dataset-creator. 
1. Ajuste o diretório da pasta com os vídeos a serem salvos/analisados no arquivo **`dataset-creator/options.json`**. -->
## Instale o Docker
1. Confira se já possui docker utilizando `docker -v` no terminal.
2. Caso não possua, execute o seguinte comando no terminal
    ``` shell
    apt update && \
    apt install -y apt-transport-https ca-certificates curl software-properties-common && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable" && \
    apt update && \
    apt-cache policy docker-ce && \
    apt install -y docker-ce
    ```
3. Em caso de erro, adicione `sudo` na frente de cada comando `apt`.
---
# Câmeras antigas - Informações importantes

- Para alterar os parâmetros de `fps`, `width`, `height` e `color` das câmeras, utlize o [options/copia_json.py](options/copia_json.py)
- O arquivo `capture_images.py` só irá mostrar as imagens das 4 câmeras com todas elas funcionando. Caso uma ou mais câmeras não estejam funcionando, o programa não irá mostrar as imagens.
- A câmera *antiga*[^1] possui uma limitação quanto ao número de frames por segundo de acordo com seu modo de cor. 
  1. Na opção **RGB** (*pixel format RGB8*) as câmeras funcionam com até **12 fps** (1288 width, 728 heigth).
  2. Na opção **GRAY** (*pixel format Mono8*) as câmeras irão funcionar com até **30 fps** (1288 width, 728 heigth). 
  3. Informações adicionais podem ser encontradas nas [referências técnicas](./referencias-tecnicas) das câmeras.
- As alterações realizadas nos arquivos `options/X.json` (sendo X = 0, 1, 2 ou 3) somente surtirão efeito ao inicializar os containers. 
  ⚠️ *Caso os containers estejam ativos e for realizado alguma mudanças nos arquivos json, os containers deverão ser parados e reinicializados.*
- Para parar todos os containers de uma só vez utilize o comando: `sudo docker container stop $(sudo docker container ls -q)`
- O Flycapture SDK, software do fabricante das câmeras, é compatível com o modelo *antigo*[^1].

- ⚠️⚠️O arquivo [options.json](dataset-creator/options.json) está vinculado às câmeras antigas e à captura de imagem, portando ele permanece sendo necessário de se atualizar quando mudar parâmetros das câmeras
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
  "O serviço <a href='https://github.com/labviros/is-skeletons-grouper'>grouper</a>, quando operado no mode Stream, consome localizações de esqueleto feitas pelo serviço <a href='https://github.com/labviros/is-skeletons-detector'>is-skeletons-detector</a> por meio do tópico <code>SkeletonsDetector.(ID).Detection</code>, agrupa as localizações 2D dos esqueletos dentro de uma janela de tempo <i>a cada 100ms por exemplo</i>, faz a reconstrução 3D e publica em outro tópico <code>SkeletonsGrouper.(GROUP_ID).Localization</code> a localização. Ele também pode operar no modo <b>RPC</b>, em que você envia um grupo de esqueletos 2D, e ele retorna as localizações 3D. Esse serviço depende do serviço de <a href='https://github.com/labviros/is-frame-transformation'>Frame Transformation</a>, e este serviço precisa da pasta com as calibrações para inicializar."
  <p>- 
      <cite>Felippe Mendonça</cite>
      <footer><time datetime="2023-05-22">22 de maio de 2023</time></footer>
  </p>
</blockquote>

# Pastas e arquivos do espaço inteligente

## root(pasta inicial do diretório)
- [iniciar_principais_containers.sh](iniciar_principais_containers.sh) - Bash para iniciar todos os containers do EI
- [visualizar_camera.py](visualizar_camera.py) - Arquivo teste para visualizar a imagem de uma câmera.
- [sh_permission_denied.py](sh_permission_denied.py) -
- [requirements.txt](requirements.txt) -
## dataset-creator

- [dataset-creator/capture_images.py](dataset-creator/capture_images.py) - Realiza a captura dos frames das 4 câmeras e os salva no diretório especificado em `/dataset-creator/options.json`. Comandos válidos: `s` inicia a gravação (salvar imagens), `p` pausa a gravação, `q` fecha o programa.

- [dataset-creator/make_videos.py](/dataset-creator/make_videos.py) - A partir dos frames capturados pelo arquivo `capture_images.py`, monta os vídeos de cada câmera e os salva em formato `.mp4`.
- [dataset-creator/request_2d.py](dataset-creator/request_2d.py) - #TODO
- [dataset-creator/request_3d.py](dataset-creator/request_3d.py) - #TODO
- [dataset-creator/options.json](dataset-creator/options.json) - Parâmetros da criação gravação e análise dos vídeos. Neste arquivo, é possível alterar o diretório onde os frames das câmeras serão salvos para posteriormente formarem vídeos. 
  
- [dataset-creator/export-video-3d-medicoes-e-erros.py](dataset-creator/export-video-3d-medicoes-e-erros.py) - Arquivo do Wyctor utilizado para realizar cálculos sobre a reconstrução 3D **Deprecated**
- [dataset-creator/Parameters.py](dataset-creator/Parameters.py) - programa que possui funções usadas no arquivo `export-video-3d-medicoes-e-erros.py`. **Deprecated**

### [calculate.py](dataset-creator/calculate.py) 
A partir do arquivo json gerado pelo `request_3d.py`, calcula as métricas e os gráficos da gravação
#### Classe Skeleton
#### Classe Calculate
##### Ângulo dos joelhos
##### Alinhamento do tronco
##### Velocidade
##### Distância
#### Classe Calculate.Vector
#### Classe Plot
#### Altura do pé

## sh_files
## is-camera-py-labtef
## calibrations

## options
- [options/X.json](options/0.json) - Parâmetros da câmera X (câmeras 0, 1, 2 e 3). Neste arquivo é possível alterar parâmetros relativos a câmera: `IP`, `fps`, `height`, `width` e etc.

# Câmeras novas do switch e o novo serviço de gateway
**❗Há problemas de conflito ao se utilizar o Spinnaker enquanto os containers das câmeras estão ativos.**

As câmeras *novas*[^2] adquiridas recentemente para o EI não funcionam com o serviço de gateway já disponível. Desta forma, [um novo serviço de gateway](https://github.com/LabTef-Ifes/is-cameras-py) foi desenvolvido. Em sua primeira utilização, execute as instruções contidas no Readme e conseguirá visualizar a imagem de uma câmera. 

Para iniciar as quatro câmeras de uma só vez, execute o comando `sudo docker compose up` dentro da pasta `deploy/multi-camera`. As configurações das câmeras podem ser alterados nos arquivos `settings-camera-X.yaml` (sendo X o id sequencial da câmera) também contidos na pasta `deploy/multi-camera`. Caso só exista o arquivo correspondente a uma câmera, crie os demais. Os parâmetros disponíveis para alteração são `fps`, `formato de cores`, `height`, `width` e `ratio`. Com os containers ativos, os arquivo do EI podem ser utilizados normalmente. Os containers que estarão ativos serão (_Name_):

| Containers(_Name_)             |            descrição |
| :----------------------------- | -------------------: |
| multi-camera-rabbitmq-1        | Comunicação RabbitMQ |
| multi-camera-is-mjpeg-server-1 |                #TODO |
| multi-camera-camera-0-1        |  Conexão da câmera 0 |
| multi-camera-camera-1-1        |  Conexão da câmera 1 |
| multi-camera-camera-2-1        |  Conexão da câmera 2 |
| multi-camera-camera-3-1        |  Conexão da câmera 3 |

- O Readme contido dentro do arquivo `spinnaker-2.7.0.128-Ubuntu18.04-amd64-pkg.tar.gz` possui informações -_sobre alteração de buffer, por exemplo_- que podem ajudar caso esteja ocorrendo algum problema de captura de imagem.
- O `Spinnaker SDK` é o software do fabricante das câmeras compatível com o modelo *novo*[^2] e com o modelo *antigo*[^1]
<!-- Aqui está Spinnaker SDK e mais acima está Flycapture SDK. Qual é o certo? -->

[^2]: modelo novo **Blackfly S GigE BFS-PGE-16S2C-CS**
## Como iniciar as câmeras

1. Conecte a câmera no Switch físico
2. Abra o software **SpinView**
3. Clique com o botão direito no IP da câmera e clique em `Auto Force IP`
4. Confira que os IP's das câmeras estão corretos nos arquivos `settings-camera-X.yaml`, dentro de [multi-camera](is-cameras-py-labtef\deploy\multi-camera)
5. Inicie os containers com o comando `python iniciar_principais_containers.sh` na pasta principal.
6. Confira que os containeres listados estão em execução
7. As câmeras foram iniciadas, visualize-as com o script `capture_images.py` executado dentro do `venv`
<!-- Necessário completar -->

# Configurações do Labtef

| Item                   |                           Detalhamento |
| :--------------------- | -------------------------------------: |
| S.O                    |                     Ubuntu 18.04.5 LTS |
| Processador            | Intel® Core™ i5-8400 CPU @ 2.80GHz × 6 |
| RAM                    |                                   16GB |
| Placa de vídeo         |      NVIDIA GeForce GTX 1070/PCIe/SSE2 |
| Placa de rede          |                       fibra ótica 10Gb |
| Versão do Python       |                                  3.6.9 |
| Switch                 |          3Com Switch 4800G PWR 24-Port |
| Portas com PoE ativado |                    19, 21, 22, 23 e 24 |

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
- [is-aruco-camera-calibration](https://github.com/LabTef-Ifes/is-aruco-camera-calibration) *Referência*
- [Camera Calibration New](https://github.com/LabTef-Ifes/camera-calibration-new) **Working**
- [Camera Calibration](https://github.com/LabTef-Ifes/camera-calibration) **Deprecated**

## Skeleton Detector
- [Skeleton Detector do Felippe Mendonça](https://github.com/labviros/is-skeletons-detector)

---
# Recomendações de estudo

- [Introdução aos conceitos do EI - CursoEI](https://github.com/LabTef-Ifes/CursoEI)
- [Github by The Coding Train](https://www.youtube.com/playlist?list=PLRqwX-V7Uu6ZF9C0YMKuns9sLDzK6zoiV)
- [Curso de Git e GitHub do CursoEmVideo](https://www.cursoemvideo.com/curso/curso-de-git-e-github/)

---

# Reiniciando o PC 20 do Labtef
Em caso de crash do pc, é necessário reiniciá-lo pelo botão físico e seguir os passos abaixo .
1. Selecione Ubuntu no menu de fundo roxo
2. digite `fsck /dev/sda1` na tela preta de terminal _⚠️atenção ao espaço_
3. aperte `y` para aceitar cada alteração
4. digite `reboot`
