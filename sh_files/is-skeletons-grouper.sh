#!/bin/bash

# Defina a quantidade de réplicas que você deseja criar
NUM_REPLICAS=4

# Defina o nome do contêiner e o nome da imagem
CONTAINER_NAME_PREFIX=grouper
IMAGE_NAME=mendonca/is-skeletons-grouper:0.0.4-debug

# Loop para criar e executar as réplicas
for i in $(seq 1 $NUM_REPLICAS); do
    # Defina o nome do contêiner com um sufixo numérico
    CONTAINER_NAME=${CONTAINER_NAME_PREFIX}$i

    # Execute o contêiner com o docker run
    nvidea-docker run -d --rm \
        -v $PWD/is-skeletons-grouper/options.json:/opt/is/options.json \
        --memory=1g \
        --cpus=1 \
        --network=host \
        --name $CONTAINER_NAME \
        $IMAGE_NAME ./service.bin /options.json

    # Aguarde um curto período antes de iniciar a próxima réplica
    sleep 0.5
done
