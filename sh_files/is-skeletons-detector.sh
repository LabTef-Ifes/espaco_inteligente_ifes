nvidia-docker run --rm -d \
  --memory=3g \
  --gpus=1 \
  --network=host \
  --name=sk1 \
  labviros/is-skeletons-detector:0.0.2-openpose ./rpc.bin
   #./stream.bin #./rpc.bin #

nvidia-docker run --rm -d \
  --memory=3g \
  --gpus=1 \
  --network=host \
  --name=sk2 \
  labviros/is-skeletons-detector:0.0.2-openpose ./rpc.bin
  #./stream.bin #./rpc.bin 

# Por que duas vezes???