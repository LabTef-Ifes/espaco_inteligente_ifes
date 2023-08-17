#!/bin/bash

# Stop all running containers
sudo docker container stop $(sudo docker container ls -q)

# Execute sh_permission_denied.py using Python
sudo python sh_permission_denied.py

# Change directory and start Docker Compose in detached mode
cd is-cameras-py-labtef/deploy/multi-camera && sudo docker compose up -d && cd ../../..

# Wait for 7 seconds
sleep 7

# Uncomment the lines below if you want to run the following scripts:
#./sh_files/is-cameras.sh
#./sh_files/is-rabbitmq.sh
#./sh_files/is-zipkin.sh
#./sh_files/is-mjpeg.sh

# Run the specified scripts
bash sh_files/is-frame-transformation.sh
sleep 1
bash sh_files/is-skeletons-grouper.sh
sleep 1
bash sh_files/is-skeletons-detector.sh
