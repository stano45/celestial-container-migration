import os
import time
from config import (
    CHECKPOINT_DIR,
    CHECKPOINT_NAME,
    REMOVE_OLD_CHECKPOINT,
)
from docker_client import DockerClient

from utils import (
    get_directory_size,
    run_command,
)


def checkpoint(container_id):
    # -----------------------------SETUP------------------------------------
    docker_client = DockerClient()
    checkpoint_name = f"{CHECKPOINT_NAME}-{container_id}"

    # Clean old checkpoints
    if REMOVE_OLD_CHECKPOINT:
        run_command(f"sudo rm -rf {CHECKPOINT_DIR}/{checkpoint_name}")
        print("Removed old checkpoint " f"{CHECKPOINT_DIR}/{checkpoint_name}.")

    container = docker_client.get_container_by_name(
        container_name=container_id
    )

    print(f"Got original container with id: {container.id}")

    # Save Redis state manually
    print("Initiating Redis background save...")
    run_command(f"docker exec -it {container.id} redis-cli save")

    # Disable Persistence in Redis
    print("Disabling Redis persistence...")
    run_command(
        f"docker exec -it {container.id} " 'redis-cli config set save ""'
    )
    run_command(
        f"docker exec -it {container.id} " "redis-cli config set appendonly no"
    )

    checkpoint_start_time = time.time()

    # Create a checkpoint
    docker_client.create_checkpoint(
        container_name=container.id,
        checkpoint_dir=CHECKPOINT_DIR,
        checkpoint_name=checkpoint_name,
    )

    checkpoint_duration = time.time() - checkpoint_start_time
    print(
        f"Checkpoint created at {CHECKPOINT_DIR}/{checkpoint_name} "
        f"in {checkpoint_duration:.2f} seconds."
    )

    checkpoint_size_bytes = get_directory_size(
        os.path.join(CHECKPOINT_DIR, checkpoint_name)
    )
    print(
        "Size of uncompressed checkpoint: "
        f"{checkpoint_size_bytes / (1024 * 1024):.2f} MB"
    )

    # Compress the checkpoint
    os.makedirs(os.path.expanduser("~/docker-checkpoints"), exist_ok=True)
    compressed_checkpoint_path = os.path.expanduser(
        f"~/docker-checkpoints/{checkpoint_name}.tar.gz"
    )
    start_time_compress = time.time()
    run_command(
        f"sudo tar -czvf {compressed_checkpoint_path} "
        f"-C {CHECKPOINT_DIR} {checkpoint_name}"
    )
    compress_duration = time.time() - start_time_compress

    print(f"Time taken to compress: {compress_duration:.2f} seconds.")
    compressed_checkpoint_size_bytes = os.path.getsize(
        compressed_checkpoint_path
    )
    print(
        "Size of compressed checkpoint: "
        f"{compressed_checkpoint_size_bytes / (1024 * 1024):.2f} MB"
    )

    return compressed_checkpoint_path
