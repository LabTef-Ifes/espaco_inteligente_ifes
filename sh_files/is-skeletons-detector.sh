nvidia-docker run --rm -d \
  --memory=2g \
  --gpus=1 \
  --network=host \
  --name=sk1 \
  labviros/is-skeletons-detector:0.0.2-openpose ./rpc.bin
   #./stream.bin #./rpc.bin #

 nvidia-docker run --rm -d \
   --memory=2g \
   --gpus=1 \
   --network=host \
   --name=sk2 \
   labviros/is-skeletons-detector:0.0.2-openpose ./rpc.bin
   #./stream.bin #./rpc.bin

# Inicia várias instâncias do detector para aumentar o poder de processamento
