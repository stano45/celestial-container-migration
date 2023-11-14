import os
import time
from server.config import (
    CHECKPOINT_DIR,
    CHECKPOINT_NAME,
)
from server.podman_client import PodmanClient

from server.utils import (
    get_file_size,
)


def checkpoint(container_id):
    podman_client = PodmanClient()

    checkpoint_dir = os.path.expanduser(CHECKPOINT_DIR)
    checkpoint_name = f"{CHECKPOINT_NAME}-{container_id}.tar.gz"
    checkpoint_path = os.path.join(checkpoint_dir, checkpoint_name)
    os.makedirs(os.path.join(checkpoint_dir), exist_ok=True)

    # Get all volumes mounted by the container before checkpointing
    volumes = podman_client.get_volume_ids_of_container(container_id)

    checkpoint_start_time = time.time()

    podman_client.create_checkpoint(
        container_id=container_id, checkpoint_path=checkpoint_path
    )

    checkpoint_duration = time.time() - checkpoint_start_time
    print(
        f"Checkpoint created at {checkpoint_path} "
        f"in {checkpoint_duration:.2f} seconds."
    )

    checkpoint_size_bytes = get_file_size(checkpoint_path)
    print(
        "Size of checkpoint: "
        f"{checkpoint_size_bytes / (1024 * 1024):.2f} MB"
    )

    # The container should not be present after checkpointing
    # but we still try to remove it just in case (ignore errors)
    podman_client.remove_container(container_id)

    # Remove the volumes created by the container,
    # otherwise we cannot start it again on this machine
    for volume_id in volumes:
        podman_client.remove_volume(volume_id)

    return checkpoint_path


if __name__ == "__main__":
    checkpoint(container_id="redis")
