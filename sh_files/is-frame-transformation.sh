docker container run -d --rm \
	-v $PWD/calibrations/ifes:/opt/ifes_calibration/ \
	-v $PWD/etc/conf/options.json:/etc/conf/options.json \
	--network=host \
	--name=is-frame_transformation \
	labviros/is-frame-transformation:0.0.4 ./service.bin /etc/conf/options.json

