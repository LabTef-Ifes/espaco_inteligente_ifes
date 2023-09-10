#!/bin/bash

# Stop and remove all running containers
sudo docker rm -f $(sudo docker container ls -q)

# Execute sh_permission_denied.py using Python
sudo python sh_permission_denied.py

# Wait for 1 second between each command
sleep 1

# Run the specified scripts one by one, waiting 1 second between each
bash sh_files/is-rabbitmq.sh
sleep 1

bash sh_files/is-zipkin.sh
sleep 1

bash sh_files/is-mjpeg.sh
sleep 1

bash sh_files/is-frame-transformation.sh
sleep 1

bash sh_files/is-skeletons-grouper.sh
sleep 1

bash sh_files/is-skeletons-detector.sh
