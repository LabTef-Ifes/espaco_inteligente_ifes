# ESPAÇO INTELIGENTE - IFES - CAMPUS VITÓRIA

![Reconstrução tridimensional](https://github.com/wyctorfogos/ESPACOINTELIGENTE-IFES/blob/main/caminhada.gif)

[Instalando o Github no Linux](https://github.com/cli/cli/blob/trunk/docs/install_linux.md)

Antes de tudo, instale as bibliotecas necessárias para o espaço inteligente e que se encontram no arquivo 'Docker_files/requiremensts.txt' através do comando 'pip install -r requirements.txt'. É recomendado utilizar um virtualenv para o espaço reservado com todas as bibliotecas desejadas.

1. Ajuste os diretórios dos arquivos is-basic.sh, is-cameras.sh, is-frame-transformation.sh e is-skeletons-grouper.sh de acordo com a sua máquina.  
2. Suba os containeres necessários para o funcionamento do espaço inteligente: execute o arquivo 'iniciar_principais_containeres.py'. Caso se depare com o erro de 'permission denied', execute o arquivo 'sh_permission_denied.py' e rode o arquivo 'iniciar_principais_containeres.py' novamente.
3. No terminal, digite 'sudo docker stats' para verificar se os containeres estão rodando (Ctrl+C para fechar). 
4. Ajuste o diretório da pasta com os vídeos a serem salvos/analisados no arquivo 'dataset-creator/options.json'.

A seguir, temos uma breve explicação de alguns arquivos do espaço inteligente.

- '/options/0.json' - parâmetros da câmera 0 (há também os parâmetros das câmeras 1, 2 e 3). Neste arquivo é possível alterar parâmetros relativos a câmera: IP, fps, altura, largura e etc.
- '/dataset-creator/options.json' - parâmetros da criação gravação e análise dos vídeos. Neste arquivo é possível alterar o diretório onde os frames das câmeras serão salvos, para posteriormente formarem vídeos. 
- '/dataset-creator/capture-images.py' - realiza a captura dos frames das 4 câmeras e os salva no diretório especificado em '/dataset-creator/options.json'. Comandos válidos: “s” inicia a gravação (salvar imagens), “p” pausa a gravação, “q” fecha o programa.
- '/dataset-creator/make-videos.py' - A partir dos frames capturados pelo arquivo 'capture-images.py', monta os vídeos e salva em formato .mp4.
- '/dataset-creator/export-video-3d-medicoes-e-erros.py' - programa principal que realiza a leitura dos pontos gerados, calcula os parâmetros frame a frame, classifica o movimento executado e mostra o vídeo.
- '/dataset-creator/parameters.py' - programa que possui funções usadas no arquivo 'export-video-3d-medicoes-e-erros.py'.
- /dataset-creator/captura-monta-e-analisa-video.py - programa para rodar todo o sistema em sequência, desde a captura até a análise.
- 'visualizar_camera.py' - arquivo teste para visualizar a imagem de somente uma câmera.

Informações importantes

- O arquivo 'capture-images.py' só irá mostrar as imagens das 4 câmeras com todas elas funcionando. Caso uma ou mais câmeras não esteja funcionando por algum motivo qualquer, o programa não irá mostrar as imagens.
- A câmera do modelo BlackFly possui uma limitação quanto ao número de frames por segundo mo que diz respeito ao modelo de cores. Na opção 'RGB' a câmera irá funcionar com até 12 fps e na opção 'GRAY' irá funcionar com até X fps.  


Em caso de dúvidas sobre os serviços ou outras questões, acesse o projeto original: https://github.com/labviros
