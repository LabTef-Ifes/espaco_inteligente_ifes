docker container run -d --rm \
	-v /home/rafael/desenvolvimento/espaco_inteligente_ifes/calibrations/ifes:/opt/ifes_calibration/ \
	-v /home/rafael/desenvolvimento/espaco_inteligente_ifes/etc/conf/options.json:/etc/conf/options.json \
	--network=host \
	--name=is-frame_transformation \
	labviros/is-frame-transformation:0.0.4 ./service.bin /etc/conf/options.json

