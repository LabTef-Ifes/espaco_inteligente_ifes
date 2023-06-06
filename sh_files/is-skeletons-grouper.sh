docker container run -ti --rm \
	-v $PWD/is-skeletons-grouper/options.json:/opt/is/options.json \
	--memory=2g \
	--cpus=1 \
	--network=host \
	--name=grouper \
	mendonca/is-skeletons-grouper:0.0.4-debug  ./rpc.bin /options.json | tee container_logs.txt
    #./service.bin /options.json 
    #./rpc.bin /options.json 