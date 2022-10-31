import docker

cli = docker.DockerClient(base_url='unix:///var/run/docker.sock')
containers = cli.containers.list(sparse = True)
print(containers)