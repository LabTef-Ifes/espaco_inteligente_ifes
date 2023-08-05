docker container run -d --rm \
	-v $PWD/is-skeletons-grouper/options.json:/opt/is/options.json \
	--memory=2g \
	--cpus=1 \
	--network=host \
	--name=grouper1 \
	mendonca/is-skeletons-grouper:0.0.4-debug  ./rpc.bin /options.json
    #./service.bin /options.json 
    #./rpc.bin /options.json 

 docker container run -d --rm \
 	-v $PWD/is-skeletons-grouper/options.json:/opt/is/options.json \
 	--memory=2g \
 	--cpus=1 \
 	--network=host \
 	--name=grouper2 \
 	mendonca/is-skeletons-grouper:0.0.4-debug  ./rpc.bin /options.json
     ./service.bin /options.json 
     #./rpc.bin /options.json 

 docker container run -d --rm \
 	-v $PWD/is-skeletons-grouper/options.json:/opt/is/options.json \
 	--memory=2g \
 	--cpus=1 \
 	--network=host \
 	--name=grouper3 \
 	mendonca/is-skeletons-grouper:0.0.4-debug  ./rpc.bin /options.json
     ./service.bin /options.json 
     #./rpc.bin /options.json 

 docker container run -d --rm \
 	-v $PWD/is-skeletons-grouper/options.json:/opt/is/options.json \
 	--memory=2g \
 	--cpus=1 \
 	--network=host \
 	--name=grouper4 \
 	mendonca/is-skeletons-grouper:0.0.4-debug  ./rpc.bin /options.json
    #./service.bin /options.json 
    #./rpc.bin /options.json 
    
