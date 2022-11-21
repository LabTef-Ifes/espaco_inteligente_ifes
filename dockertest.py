import docker
from time import sleep


# Checks if the containers are running, if not, it starts them

# cli = docker.DockerClient(base_url='unix:///var/run/docker.sock')
# containers = cli.containers.list(sparse=True)

def is_container_running(container_name: str):
    """Verify the status of a container by it's name

    :param container_name: the name of the container
    :return: boolean or None
    """
    RUNNING = "running"
    # Connect to Docker using the default socket or the configuration
    # in your environment
    docker_client = docker.from_env()
    # Or give configuration
    # docker_socket = "unix://var/run/docker.sock"
    # docker_client = docker.DockerClient(docker_socket)

    try:
        container = docker_client.containers.get(container_name)
    except docker.errors.NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
    else:
        container_state = container.attrs["State"]
        return container_state["Status"] == RUNNING


if __name__ == "__main__":
    containeres = ['rabbitmq', 'zipkin', 'cam0', 'cam1', 'cam2', 'cam3',
                   'sk1', 'sk2', 'is-frame_transformation', 'grouper']
    for c in containeres:
        result = is_container_running(c)
        print(c, result)
        if not result:
            down_containeres.append(c)

    while down_containeres:
        sleep(3)
        for c in down_containeres:
            result = is_container_running(c)
            print(c, result)
            if result:
                down_containeres.remove(c)
