# ESPAÇO INTELIGENTE LABTEF - IFES CAMPUS VITÓRIA

![Reconstrução tridimensional](https://github.com/wyctorfogos/ESPACOINTELIGENTE-IFES/blob/main/caminhada.gif)

---
[Instalando o Github no Linux](https://github.com/cli/cli/blob/trunk/docs/install_linux.md)

**Para utilizar o GitHub no Linux, é recomendado utilizar a extensão github nativa no VsCode**
Para sincronizar esse repositório à uma pasta local na sua máquina Linux, abra o terminal e digite `git clone https://github.com/LabTef-Ifes/espaco_inteligente_ifes` para o repositório principal ou `git clone https://github.com/LabTef-Ifes/espaco_inteligente_ifes-deivid` para o fork de atualização.

É recomendado utilizar um virtualenv para o espaço reservado com todas as bibliotecas desejadas.
Para criar um venv, digite `python3 -m venv nomedovenv` no diretório reservado ao projeto

Instale as bibliotecas necessárias para o espaço inteligente, descritas no arquivos [requirements.txt](requirements.txt) através do comando `pip install -r requirements.txt`.

1. Ajuste os diretórios dos arquivos is-basic.sh, is-cameras.sh, is-frame-transformation.sh e is-skeletons-grouper.sh de acordo com a sua máquina.
2. Suba os containeres necessários para o funcionamento do espaço inteligente: execute o arquivo [iniciar_principais_containeres.py](iniciar_principais_containeres.py). Caso se depare com o erro de **permission denied**, execute o arquivo [sh_permission_denied.py](sh_permission_denied.py) e execute o arquivo [iniciar_principais_containeres.py](iniciar_principais_containeres.py) novamente.
3. No terminal, digite `sudo docker stats` para verificar se os containeres estão rodando (*Ctrl+C para fechar*). 
4. Ajuste o diretório da pasta com os vídeos a serem salvos/analisados no arquivo **dataset-creator/options.json**.

---
A seguir, temos uma breve explicação de alguns arquivos do espaço inteligente.

- [options/0.json](options/0.json) - parâmetros da câmera 0 (há também os parâmetros das câmeras 1, 2 e 3). Neste arquivo é possível alterar parâmetros relativos a câmera: IP, fps, altura, largura e etc.
- [dataset-creator/options.json](dataset-creator/options.json) - parâmetros da criação gravação e análise dos vídeos. Neste arquivo é possível alterar o diretório onde os frames das câmeras serão salvos, para posteriormente formarem vídeos. 
- [dataset-creator/capture-images.py](dataset-creator/capture-images.py) - realiza a captura dos frames das 4 câmeras e os salva no diretório especificado em '/dataset-creator/options.json'. Comandos válidos: “s” inicia a gravação (salvar imagens), “p” pausa a gravação, “q” fecha o programa.
- [dataset-creator/make-videos.py](/dataset-creator/make-videos.py) - A partir dos frames capturados pelo arquivo 'capture-images.py', monta os vídeos e os salva em formato .mp4.
- [dataset-creator/export-video-3d-medicoes-e-erros.py](dataset-creator/export-video-3d-medicoes-e-erros.py) - programa principal que realiza a leitura dos pontos gerados, calcula os parâmetros frame a frame, classifica o movimento executado e mostra o vídeo.
- [dataset-creator/parameters.py](dataset-creator/parameters.py) - programa que possui funções usadas no arquivo 'export-video-3d-medicoes-e-erros.py'.
- [dataset-creator/captura-monta-e-analisa-video.py](dataset-creator/captura-monta-e-analisa-video.py) - programa para executar todo o sistema em sequência, desde a captura até a análise.
- [visualizar_camera.py](visualizar_camera.py) - arquivo teste para visualizar a imagem de somente uma câmera.

**Informações importantes**

- Para alterar os parâmetros de fps, width, height e color das câmeras, utlize o [options/copia_json.py](options/copia_json.py)
- O arquivo **capture-images.py** só irá mostrar as imagens das 4 câmeras com todas elas funcionando. Caso uma ou mais câmeras não esteja funcionando por algum motivo qualquer, o programa não irá mostrar as imagens.
- A câmera do modelo BlackFly (Blackfly GigE BFLY-PGE-09S2C) possui uma limitação quanto ao número de frames por segundo no que diz respeito ao modelo de cores. Na opção **RGB** (pixel format RGB8) as câmeras irão funcionar com até _12_ fps (1288 width, 728 heigth) e na opção **GRAY** (pixel format Mono8) as câmeras irão funcionar com até _30_ fps (1288 width, 728 heigth). Informações adicionais podem ser encontradas nas [referências técnicas](./referencias-tecnicas/)  das câmeras.
- As alterações realizadas nos arquivos options/X.json (sendo X = 0, 1, 2 ou 3) somente surtirão efeito ao inicializar os containers. Caso os containers estejam ativos e for realizado alguma mudanças nos arquivos .json, os containers deverão ser parados e reinicializados.
- Para parar todos os conteiners de uma só vez utilize o comando: `sudo docker container stop $(sudo docker container ls -q)`
- O espaço inteligente atual do Ifes no  roda em uma máquina Ubuntu 18.04.5 LTS, processador Intel® Core™ i5-8400 CPU @ 2.80GHz × 6, 16Gb de memória, placa de vídeo NVIDIA GeForce GTX 1070/PCIe/SSE2 e uma placa de rede fibra ótica 10Gb.   

**Câmeras novas e o novo serviço de gateway**

As câmeras (Blackfly S GigE BFS-PGE-16S2C-CS) adquiridas recentemente para o espaço inteligente não funcionam com o serviço de gateway já disponível. Desta forma, uma novo serviço de gateway foi desenvolvido e pode ser encontrado [aqui](https://github.com/LabTef-Ifes/is-cameras-py). Em sua primeira utilização, execute as instruções contidas no readme e conseguirá visualisar a imagem de uma câmera. Para rodar a quatro câmeras de uma só vez, execute o comando `sudo docker compose up` dentro da pasta deploy/multi-camera. As configurações das câmeras podem ser alterados nos arquivos settings-camera-X.yaml (sendo X = 0, 1, 2 ou 3) também contidos na pasta deploy/multi-camera. Caso só exista o arquivo correspondeste a uma câmera, você poderá criar os demais. Os parâmetros disponíveis para alteração são fps e mapa de cores.

Em caso de dúvidas sobre os serviços ou outras questões, acesse o projeto original: [LabViros](https://github.com/labviros)
