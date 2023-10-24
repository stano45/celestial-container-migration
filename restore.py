import time
from config import CLEANUP_OLD_CONTAINERS
from docker_client import DockerClient

from utils import (
    run_command,
)


def restore(
    container_name: str, checkpoint_file_path: str, checkpoint_name: str
):
    docker_client = DockerClient()

    if CLEANUP_OLD_CONTAINERS:
        docker_client.remove_container_by_name(container_name)

    restore_start_time = time.time()
    container = docker_client.create_redis_container(
        container_name=container_name,
    )

    # Decompress and move the checkpoint to the cloned container
    # This is a workaround, see:
    # https://github.com/moby/moby/issues/37344#issuecomment-450782189
    run_command(
        f"sudo tar -xzvf {checkpoint_file_path} "
        f"-C /var/lib/docker/containers/{container.id}/checkpoints/"
    )

    # Start the new container from the checkpoint
    docker_client.start_redis_container_from_checkpoint(
        container_id=container.id, checkpoint_name=checkpoint_name
    )

    print("Cloned container started from checkpoint.")
    restore_duration = time.time() - restore_start_time
    print(f"Restore time: {restore_duration:.2f} seconds.")
