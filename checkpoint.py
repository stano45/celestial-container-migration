import os
import time
from config import (
    CHECKPOINT_DIR,
    CHECKPOINT_NAME,
    ORIGINAL_REDIS_CONTAINER_NAME,
    REMOVE_OLD_CHECKPOINT,
)
from docker_client import DockerClient

from utils import (
    get_directory_size,
    run_command,
)


def checkpoint(container_name):
    # -----------------------------SETUP------------------------------------
    docker_client = DockerClient()

    # Clean old checkpoints
    if REMOVE_OLD_CHECKPOINT:
        run_command(f"sudo rm -rf {CHECKPOINT_DIR}/{CHECKPOINT_NAME}")
        print("Removed old checkpoint " f"{CHECKPOINT_DIR}/{CHECKPOINT_NAME}.")

    # Create and start original container
    print(
        "Starting original container... "
        "(This might take a while the first time)"
    )

    original_container = docker_client.get_container_by_name(
        container_name=container_name
    )

    print(f"Got original container with id: {original_container.id}")

    # Save Redis state manually
    print("Initiating Redis background save...")
    run_command(f"docker exec {ORIGINAL_REDIS_CONTAINER_NAME} redis-cli save")

    # Disable Persistence in Redis
    print("Disabling Redis persistence...")
    run_command(
        f"docker exec {ORIGINAL_REDIS_CONTAINER_NAME} "
        'redis-cli config set save ""'
    )
    run_command(
        f"docker exec {ORIGINAL_REDIS_CONTAINER_NAME} "
        "redis-cli config set appendonly no"
    )

    checkpoint_start_time = time.time()

    # Create a checkpoint
    docker_client.create_checkpoint(
        container_name=ORIGINAL_REDIS_CONTAINER_NAME,
        checkpoint_dir=CHECKPOINT_DIR,
        checkpoint_name=CHECKPOINT_NAME,
    )

    checkpoint_duration = time.time() - checkpoint_start_time
    print(
        f"Checkpoint created at {CHECKPOINT_DIR}/{CHECKPOINT_NAME} "
        f"in {checkpoint_duration:.2f} seconds."
    )

    original_container.stop()
    original_container.remove()
    # time.sleep(2)

    # Get and print checkpoint size (uncompressed)
    checkpoint_size_bytes = get_directory_size(
        os.path.join(CHECKPOINT_DIR, CHECKPOINT_NAME)
    )
    print(
        "Size of uncompressed checkpoint: "
        f"{checkpoint_size_bytes / (1024 * 1024):.2f} MB"
    )

    # Compress the checkpoint
    start_time_compress = time.time()  # Start time for compressing
    os.makedirs(os.path.expanduser("~/docker-checkpoints"), exist_ok=True)
    run_command(
        f"sudo tar -czvf ~/docker-checkpoints/{CHECKPOINT_NAME}.tar.gz "
        f"-C {CHECKPOINT_DIR} {CHECKPOINT_NAME}"
    )
    compress_duration = time.time() - start_time_compress
    compressed_checkpoint_size_bytes = os.path.getsize(
        os.path.expanduser(f"~/docker-checkpoints/{CHECKPOINT_NAME}.tar.gz")
    )
    print(
        "Size of compressed checkpoint: "
        f"{compressed_checkpoint_size_bytes / (1024 * 1024):.2f} MB"
    )
    print(f"Time taken to compress: {compress_duration:.2f} seconds.")

    return os.path.expanduser(f"~/docker-checkpoints/{CHECKPOINT_NAME}.tar.gz")
