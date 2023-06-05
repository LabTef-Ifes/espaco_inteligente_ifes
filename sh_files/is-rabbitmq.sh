echo 'rabbitmq:3.7.6-management'
docker container run --rm -d \
    -v $PWD/is-k8s-deployments/ifes:/etc/rabbitmq/  \
    -p 5672:5672 \
    -p 15672:15672 \
    --network=host \
    --name rabbitmq \
    rabbitmq:3.7.6-management
