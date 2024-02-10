docker run -it --rm --name venv --network host -v /var/run/docker.sock:/var/run/docker.sock -v ${PWD}:/app smarzarocom/env_is
