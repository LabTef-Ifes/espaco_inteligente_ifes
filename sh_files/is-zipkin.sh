echo ' openzipkin/zipkin'
docker container run --rm -d \
    -p 9411:9411 \
    --network=host \
    --name zipkin \
    openzipkin/zipkin


