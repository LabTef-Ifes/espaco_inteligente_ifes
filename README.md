# ESPAÇO INTELIGENTE LABTEF - IFES CAMPUS VITÓRIA

![Reconstrução tridimensional](caminhada.gif)

---
# Preparando o ambiente

**Para utilizar o GitHub no Linux, é recomendado utilizar a extensão github nativa no VsCode**

1. Crie uma pasta local para o projeto com o nome `desenvolvimento`
	- Para sincronizar esse repositório à uma pasta local na sua máquina Linux, abra o terminal e digite `git clone https://github.com/LabTef-Ifes/espaco_inteligente_ifes` para o repositório principal ou `git clone https://github.com/LabTef-Ifes/espaco_inteligente_ifes-deivid` para clonar o fork de atualização.
	
	- É recomendado utilizar um virtualenv reservado para todas as bibliotecas desejadas no espaço inteligente.

	- Para criar um venv, digite `python3 -m venv nomedovenv` no diretório reservado ao projeto.
1. Com o venv ativo, instale as bibliotecas necessárias para o espaço inteligente (EI) escritas no arquivos [requirements.txt](requirements.txt) através do comando `pip install -r requirements.txt`.
1. Ajuste os diretórios dos arquivos `is-basic.sh`, `is-cameras.sh`, `is-frame-transformation.sh` e `is-skeletons-grouper.sh` de acordo com a sua máquina.
1. Suba os containers necessários para o funcionamento do EI: execute o arquivo [iniciar_principais_containers.py](iniciar_principais_containers.py). Caso se depare com o erro de **permission denied**, execute o arquivo [sh_permission_denied.py](sh_permission_denied.py) e execute o arquivo [iniciar_principais_containers.py](iniciar_principais_containers.py) novamente.
1. Em outro terminal, digite `sudo docker stats` para verificar se os containers estão rodando (*Ctrl+C para fechar*). Os containers em funcionamento do EI são (verificar o parâmetro _NAME_ no terminal):
   
  | containers ativos       |
  | :---------------------- |
  | rabbitmq                |
  | zipkin                  |
  | cam0                    |
  | cam1                    |
  | cam2                    |
  | cam3                    |
  | sk1                     |
  | sk2                     |
  | is-frame_transformation |
  | grouper                 |
2. Ajuste o diretório da pasta com os vídeos a serem salvos/analisados no arquivo **`dataset-creator/options.json`**.
---
# Descrição de alguns arquivos do espaço inteligente.

- [options/0.json](options/0.json) - parâmetros da câmera 0 (há também os parâmetros das câmeras 1, 2 e 3). Neste arquivo é possível alterar parâmetros relativos a câmera: IP, fps, altura, largura e etc.
- [dataset-creator/options.json](dataset-creator/options.json) - parâmetros da criação gravação e análise dos vídeos. Neste arquivo é possível alterar o diretório onde os frames das câmeras serão salvos, para posteriormente formarem vídeos. 
- [dataset-creator/capture-images.py](dataset-creator/capture-images.py) - realiza a captura dos frames das 4 câmeras e os salva no diretório especificado em '/dataset-creator/options.json'. Comandos válidos: `s` inicia a gravação (salvar imagens), `p` pausa a gravação, `q` fecha o programa.
- [dataset-creator/make-videos.py](/dataset-creator/make-videos.py) - A partir dos frames capturados pelo arquivo `capture-images.py`, monta os vídeos e os salva em formato .mp4.
- [dataset-creator/export-video-3d-medicoes-e-erros.py](dataset-creator/export-video-3d-medicoes-e-erros.py) - programa principal que realiza a leitura dos pontos gerados, calcula os parâmetros frame a frame, classifica o movimento executado e exibe o vídeo.
- [dataset-creator/Parameters.py](dataset-creator/Parameters.py) - programa que possui funções usadas no arquivo `export-video-3d-medicoes-e-erros.py`.
- [dataset-creator/captura_monta_e_analisa_video.py](dataset-creator/captura_monta_e_analisa_video.py) - programa para executar todo o sistema em sequência, desde a captura até a análise final.
- [visualizar_camera.py](visualizar_camera.py) - arquivo teste para visualizar a imagem de somente uma câmera.

# Informações importantes

- Para alterar os parâmetros de `fps`, `width`, `height` e `color` das câmeras, utlize o [options/copia_json.py](options/copia_json.py)
- O arquivo **capture-images.py** só irá mostrar as imagens das 4 câmeras com todas elas funcionando. Caso uma ou mais câmeras não esteja funcionando, o programa não irá mostrar as imagens.
- A câmera modelo **Blackfly GigE BFLY-PGE-09S2C** possui uma limitação quanto ao número de frames por segundo de acordo com seu modo de cor. 
  1. Na opção **RGB** (*pixel format RGB8*) as câmeras funcionam com até **12 fps** (1288 width, 728 heigth).
  1. Na opção **GRAY** (*pixel format Mono8*) as câmeras irão funcionar com até **30 fps** (1288 width, 728 heigth). 
  1. Informações adicionais podem ser encontradas nas [referências técnicas](./referencias-tecnicas/) das câmeras.
- As alterações realizadas nos arquivos `options/X.json` (sendo X = 0, 1, 2 ou 3) somente surtirão efeito ao inicializar os containers. 
  Caso os containers estejam ativos e for realizado alguma mudanças nos arquivos .json, os containers deverão ser parados e reinicializados.
- Para parar todos os containers de uma só vez utilize o comando: `sudo docker container stop $(sudo docker container ls -q)`
- O Flycapture SDK é o software do fabricante das câmeras e é compatível com o modelo Blackfly GigE BFLY-PGE-09S2C. Há problemas de conflito ao se utilizar o Flycapture enquanto os containers do EI estão ativos.

# Câmeras novas do switch e o novo serviço de gateway

As câmeras **Blackfly S GigE BFS-PGE-16S2C-CS** adquiridas recentemente para o EI não funcionam com o serviço de gateway já disponível. Desta forma, [um novo serviço de gateway](https://github.com/LabTef-Ifes/is-cameras-py) foi desenvolvido. Em sua primeira utilização, execute as instruções contidas no readme e conseguirá visualizar a imagem de uma câmera. 

Para iniciar as quatro câmeras de uma só vez, execute o comando `sudo docker compose up` dentro da pasta `deploy/multi-camera`. As configurações das câmeras podem ser alterados nos arquivos `settings-camera-X.yaml` (sendo X = 0, 1, 2 ou 3) também contidos na pasta `deploy/multi-camera`. Caso só exista o arquivo correspondeste a uma câmera, crie os demais. Os parâmetros disponíveis para alteração são `fps` e `formato de cores`. Com os containers ativos, os arquivo do EI (Ex: capture-images.py) podem ser utilizados normalmente. Os containers que estarão ativos serão (_NAME_):

| Name                           |
| :----------------------------- |
| multi-camera-rabbitmq-1        |
| multi-camera-is-mjpeg-server-1 |
| multi-camera-camera-0-1        |
| multi-camera-camera-1-1        |
| multi-camera-camera-2-1        |
| multi-camera-camera-3-1        |

- Ao conectar as câmeras no switch, o endereço de IP **não estará configurado corretamente** para corresponder ao adaptador host ao qual a câmera está conectada. Para que o endereço de IP esteja corretamente configurado, abra o SpinView e force o endereço de IP automaticamente clicando com o botão direito em cima da câmera detectada pelo software e em seguida clique em `Auto Force IP`.
- O Readme contido dentro do arquivo `spinnaker-2.7.0.128-Ubuntu18.04-amd64-pkg.tar.gz` possui informações -_sobre alteração de buffer, por exemplo_- que podem ajudar caso esteja ocorrendo algum problema de captura de imagem.
- O `Spinnaker SDK` é o software do fabricante das câmeras compatível com o modelo Blackfly S GigE BFS-PGE-16S2C-CS e com o Blackfly GigE BFLY-PGE-09S2C.

❗Há problemas de conflito ao se utilizar o Spinnaker enquanto os containers do EI estão ativos.

## Como iniciar as câmeras

1. Conecte a câmera no Switch físico
2. Abra o software **SpinView**
## Repositório do gateway das novas câmeras
[Spinnaker Gateway do Felippe Mendonça](https://github.com/LabTef-Ifes/is-cameras-py)
# Configurações do Labtef

| Item                   |                           Detalhamento |
| :--------------------- | -------------------------------------: |
| S.O                    |                     Ubuntu 18.04.5 LTS |
| Processador            | Intel® Core™ i5-8400 CPU @ 2.80GHz × 6 |
| RAM                    |                                   16GB |
| Placa de vídeo         |      NVIDIA GeForce GTX 1070/PCIe/SSE2 |
| Placa de rede          |                       fibra ótica 10Gb |
| Versão do Python       |                         2.7.17 e 3.6.9 |
| Switch                 |          3Com Switch 4800G PWR 24-Port |
| Portas com PoE ativado |                    19, 21, 22, 23 e 24 |

# Referências

- Em caso de dúvidas sobre os serviços ou outras questões, acesse o projeto original: [LabViros](https://github.com/labviros)
- [Repositório do Wyctor](https://github.com/wyctorfogos/ESPACOINTELIGENTE-IFES)
## Calibração das câmeras

- Acesse o repositório [is-aruco-camera-calibration](https://github.com/LabTef-Ifes/is-aruco-camera-calibration)
- Acesse o repositório [Camera Calibration New](https://github.com/LabTef-Ifes/camera-calibration-new)
- Acesse o repositório [Camera Calibration](https://github.com/LabTef-Ifes/camera-calibration) **Deprecated**

# Reiniciando o PC 20 do Labtef
Em caso de crash do pc, é necessário reiniciá-lo pelo botão físico e seguir os passos abaixo .
1. Selecione Ubuntu no menu de fundo roxo
2. digite `fsck /dev/sda1` na tela preta de inicialização _atenção ao espaço_
3. aperte `y` para aceitar cada alteração
4. digite `reboot`

---
# Recomendações de estudo

- [CursoEI](https://github.com/LabTef-Ifes/CursoEI)
- [Github by The Coding Train](https://www.youtube.com/playlist?list=PLRqwX-V7Uu6ZF9C0YMKuns9sLDzK6zoiV)
- [Curso de Git e GitHub do CursoEmVideo](https://www.cursoemvideo.com/curso/curso-de-git-e-github/)
