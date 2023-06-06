echo 'viros/is-mjpeg-server:1'

docker run -d --name is-mjpeg-server \
    -p 3000:3000 \
    -e IS_URI=amqp://guest:guest@rabbitmq:5672 \
    --restart always \
    labviros/is-mjpeg-server:0.0.1


echo 'google-chrome http://localhost:3000/0'
