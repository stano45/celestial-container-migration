import json
import os
import time
from config import (
    CHECKPOINT_DIR,
    CHECKPOINT_NAME,
    CLEANUP_OLD_CONTAINERS,
    CLONE_REDIS_CONTAINER_NAME,
    ORIGINAL_REDIS_CONTAINER_NAME,
    RANDOM_DATA_JSON_PATH,
    RANDOM_DATA_VOLUME_NAME,
    REGENERATE_RANDOM_DATA,
    REMOVE_OLD_CHECKPOINT,
    USED_CONTAINERS,
)
from docker_client import DockerClient
from redis_client import RedisClient

from utils import (
    get_directory_size,
    run_command,
)

from generate_random_data import generate_redis_dump


def main():
    # -----------------------------SETUP------------------------------------
    docker_client = DockerClient()

    # Kill and remove any old containers
    if CLEANUP_OLD_CONTAINERS:
        for container_name in USED_CONTAINERS:
            docker_client.remove_container_by_name(container_name)

    # Clean old checkpoints
    if REMOVE_OLD_CHECKPOINT:
        run_command(f"sudo rm -rf {CHECKPOINT_DIR}/{CHECKPOINT_NAME}")
        print("Removed old checkpoint " f"{CHECKPOINT_DIR}/{CHECKPOINT_NAME}.")

    # Check if the appendonlydir exists in the volume
    if (
        REGENERATE_RANDOM_DATA is True
        or not docker_client.check_appendonlydir_exist_in_volume(
            RANDOM_DATA_VOLUME_NAME
        )
    ):
        print("Generating Redis dump...")
        generate_redis_dump()

    # -----------------------------CHECKPOINT---------------------------

    # Create and start original container
    print(
        "Starting original container... "
        "(This might take a while the first time)"
    )
    run_container_start_time = time.time()

    original_container = docker_client.run_redis_container(
        volume_name=RANDOM_DATA_VOLUME_NAME,
        container_name=ORIGINAL_REDIS_CONTAINER_NAME,
    )

    run_container_duration = time.time() - run_container_start_time
    print(
        f"Original container started with ID: {original_container.id} "
        f"in {run_container_duration:.2f} seconds."
    )

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

    # -----------------------------RESTORE----------------------------------

    # Create a new container
    restore_start_time = time.time()
    cloned_container = docker_client.create_redis_container(
        container_name=CLONE_REDIS_CONTAINER_NAME,
        volume_name=RANDOM_DATA_VOLUME_NAME,
    )

    # Decompress and move the checkpoint to the cloned container
    # This is a workaround, see:
    # https://github.com/moby/moby/issues/37344#issuecomment-450782189
    # run_command(
    #     f"sudo tar -xzvf ~/docker-checkpoints/{CHECKPOINT_NAME}.tar.gz "
    #     f"-C /var/lib/docker/containers/{clone_container_id}/checkpoints/"
    # )

    run_command(
        f"sudo mv "
        f"{CHECKPOINT_DIR}/{CHECKPOINT_NAME} "
        f"/var/lib/docker/containers/{cloned_container.id}/"
        f"checkpoints/"
    )

    # Start the new container from the checkpoint
    docker_client.start_redis_container_from_checkpoint(
        container_id=cloned_container.id, checkpoint_name=CHECKPOINT_NAME
    )

    print("Cloned container started from checkpoint.")
    restore_duration = time.time() - restore_start_time
    print(f"Restore time: {restore_duration:.2f} seconds.")
    print(
        f"C/R total time: "
        f"{checkpoint_duration + restore_duration:.2f} seconds."
    )

    # Verify the data in the cloned container
    print("Verifying data in the cloned container...")
    # Verify the data in the new Redis container
    with open(RANDOM_DATA_JSON_PATH, "r") as file:
        data = json.load(file)
        redis_client = RedisClient(
            docker_client.get_container_ip(cloned_container.id)
        )
        redis_client.verify_data(data)
        print("All data verified in the cloned container.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(str(e))
