import json
import os
import random
import string
import time
from docker_client import DockerClient

from utils import (
    DATA_JSON_PATH,
    run_command,
)

from generate_random_data import generate_redis_dump

REGENERATE_DATA = False
KILL_OLD_CONTAINERS = True
CLEAN_OLD_CHECKPOINT = True
DATA_SIZE_MB = 10
KEYS_COUNT = 100
BYTES_PER_KEY = (DATA_SIZE_MB * 1024 * 1024) // KEYS_COUNT
CHECKPOINT_DIR = "/tmp"
CHECKPOINT_NAME = "checkpoint-redis"
VOLUME_NAME = "redis_data_volume"


def generate_random_string(bytes):
    """Generate a random string of given length."""
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(bytes)
    )


def write_data_into_redis(container_id, keys_count, bytes_per_key):
    data = {}
    for i in range(1, keys_count + 1):
        key = f"key{i}"
        value = generate_random_string(bytes_per_key)
        run_command(f"docker exec {container_id} redis-cli set {key} {value}")
        data[key] = value
    return data


def verify_data_in_cloned_container(container_id, data):
    for key, original_value in data.items():
        clone_value = run_command(
            f"docker exec {container_id} redis-cli get {key}"
        )
        if original_value != clone_value:
            raise RuntimeError(
                f"Data mismatch for key {key} between saved data and ",
                "cloned container!",
            )


def get_directory_size(path):
    """Returns the size of a directory in bytes."""
    size_output = run_command(f"sudo du -sb {path}")
    size_in_bytes, _ = size_output.split("\t", 1)
    return int(size_in_bytes)


def main():
    # -----------------------------SETUP------------------------------------
    docker_client = DockerClient()

    # Kill and remove any old containers
    if KILL_OLD_CONTAINERS:
        docker_client.remove_all_redis_containers()

    # Clean old checkpoints
    if CLEAN_OLD_CHECKPOINT:
        run_command(f"sudo rm -rf {CHECKPOINT_DIR}/{CHECKPOINT_NAME}")
        print(
            "Successfully removed old checkpoint "
            f"{CHECKPOINT_DIR}/{CHECKPOINT_NAME}."
        )

    # Check if the appendonlydir exists in the volume
    if (
        REGENERATE_DATA
        or not docker_client.check_appendonlydir_exist_in_volume(VOLUME_NAME)
    ):
        print("Generating Redis dump...")
        generate_redis_dump()

    # -----------------------------CHECKPOINT---------------------------

    # Create and start original container
    print(
        "Starting original container... "
        "(This might take a while the first time)\n"
    )
    run_container_start_time = time.time()
    container_id = run_command(
        "docker run -d --name redis "
        f"-v {VOLUME_NAME}:/data "
        "--security-opt seccomp:unconfined "
        "redis:latest "
        " --appendonly yes"
    )
    run_container_duration = time.time() - run_container_start_time
    print(
        f"Original container started with ID: {container_id} "
        f"in {run_container_duration:.2f} seconds."
    )
    print("Waiting 5sec for the container to start...")
    time.sleep(5)

    # Save Redis state manually
    print("Initiating Redis background save...")
    run_command("docker exec redis redis-cli bgsave")

    # Disable Persistence in Redis
    print("Disabling Redis persistence...")
    run_command('docker exec redis redis-cli config set save ""')
    run_command("docker exec redis redis-cli config set appendonly no")

    # # Write data into the original container
    # print(f"Writing {DATA_SIZE_MB} MB of data into Redis...")
    # write_data_start_time = time.time()
    # data = write_data_into_redis(container_id, KEYS_COUNT, BYTES_PER_KEY)
    # write_data_duration = time.time() - write_data_start_time
    # print(
    #     f"Successfully written {DATA_SIZE_MB} MB of data into Redis"
    #     f" in {write_data_duration:.2f} seconds."
    # )
    # Create a checkpoint
    checkpoint_start_time = time.time()

    run_command(
        f"docker checkpoint create "
        f"--checkpoint-dir={CHECKPOINT_DIR} "
        f"redis {CHECKPOINT_NAME}"
    )
    checkpoint_duration = time.time() - checkpoint_start_time
    print(
        f"Checkpoint created at {CHECKPOINT_DIR}/{CHECKPOINT_NAME} "
        f"in {checkpoint_duration:.2f} seconds."
    )

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
    clone_container_id = run_command(
        "docker create --name redis-clone --security-opt seccomp:unconfined "
        "redis:latest "
        "--appendonly yes"
    )
    print(f"Cloned container created with ID: {clone_container_id}")

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
        f"/var/lib/docker/containers/{clone_container_id}/"
        f"checkpoints/"
    )

    # Start the new container from the checkpoint
    print("Starting new container from checkpoint...")
    run_command(
        f"sudo docker start --checkpoint={CHECKPOINT_NAME} redis-clone"
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
    with open(DATA_JSON_PATH, "r") as file:
        data = json.load(file)
        verify_data_in_cloned_container(clone_container_id, data)
        print("All data successfully verified in the cloned container.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(str(e))
