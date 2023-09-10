# Use a imagem oficial do Ubuntu 18.04 como imagem base
FROM ubuntu:18.04

LABEL org.opencontainers.image.authors="Deivid Braian"

# Atualize os pacotes do sistema e instale as dependências
RUN apt-get update && apt-get install -y \
    python3.6=3.6.9-1~18.04ubuntu1.5 \
    python3-pip \
    && apt-get clean

# Crie um link simbólico para python3.6 como python3
RUN ln -s /usr/bin/python3.6 /usr/bin/python3

# Atualize o pip para a versão mais recente
RUN python3 -m pip install --upgrade pip

# Defina a variável de ambiente LC_ALL como C.UTF-8
ENV LC_ALL=C.UTF-8

# Verifique a instalação do Python
RUN python3 --version

# Crie um diretório de trabalho
WORKDIR /app

# Copie os arquivos do seu projeto para o diretório de trabalho
# Primeiro, testa copiar TUDO e depois só o necessário
COPY .. /app

#COPY ../requirements.txt /app
#COPY ../dataset-creator /app/dataset-creator
#COPY ../calibrations /app/calibrations
# Instale as dependências do seu projeto
RUN pip install -r requirements.txt
VOLUME [ "/app" ]
# Defina o comando de inicialização (substitua pelo comando do seu aplicativo)
#CMD ["python3"]
