# Use a imagem oficial do Ubuntu 18.04 como imagem base
FROM ubuntu:18.04

LABEL org.opencontainers.image.authors="Smarzarocom"

# Atualize os pacotes do sistema e instale as dependências
RUN apt-get update && apt-get install -y \
    python3.6 \
    python3-pip \
    && apt-get clean

# Instala dependências do OpenCV
RUN apt install -y libsm6 libxext6 \
    ffmpeg

RUN apt-get install -y libxrender-dev

# Atualize o pip para a versão mais recente
RUN python3 -m pip install --upgrade pip

# Defina um alias para 'python' apontando para 'python3'
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1

# Defina a variável de ambiente LC_ALL como C.UTF-8
ENV LC_ALL=C.UTF-8

# Instale o Docker Client
RUN apt update && \
    apt install -y apt-transport-https ca-certificates curl software-properties-common && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable" && \
    apt update && \
    apt-cache policy docker-ce && \
    apt install -y docker-ce

COPY requirements.txt /app/requirements.txt
# Crie um diretório de trabalho 
WORKDIR /app
#RUN apt install -y python3-tk && \
#    apt-get install -y libsm6 libxext6 libxrender-dev

# Copia o arquivo de requisitos para o diretório de trabalho
RUN pip install -r requirements.txt
EXPOSE 80
VOLUME [ "/app" ]
# Defina o comando de inicialização (substitua pelo comando do seu aplicativo)
#CMD [""]