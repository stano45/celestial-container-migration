import time
from config import CLEANUP_OLD_CONTAINERS
from podman_client import PodmanClient


def restore(container_name: str, checkpoint_file_path: str):
    podman_client = PodmanClient()

    if CLEANUP_OLD_CONTAINERS:
        podman_client.stop_and_remove_container(container_name)

    restore_start_time = time.time()

    # Start the new container from the checkpoint
    podman_client.run_container_from_checkpoint(
        checkpoint_path=checkpoint_file_path
    )

    restore_duration = time.time() - restore_start_time
    print(f"Restore time: {restore_duration:.2f} seconds.")


if __name__ == "__main__":
    restore("redis", "/tmp/podman-checkpoint-redis.tar.gz")
