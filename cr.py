import os
import subprocess
import random
import string
import time


DATA_SIZE_MB = 100
KEYS_COUNT = 1000
BYTES_PER_KEY = (DATA_SIZE_MB * 1024 * 1024) // KEYS_COUNT
CHECKPOINT_DIR = "/tmp"
CHECKPOINT_NAME = "checkpoint-redis"


def run_command(command):
    """Execute the command and return its output."""
    result = subprocess.run(
        command, capture_output=True, text=True, shell=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Error executing command: {command}\n{result.stderr}"
        )
    return result.stdout.strip()


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
    # Create and start original container
    container_id = run_command(
        "docker run -d --name redis --security-opt seccomp:unconfined "
        "redis/redis-stack-server:latest"
    )
    print(f"Original container started with ID: {container_id}")

    # Write data into the original container
    print(f"Writing {DATA_SIZE_MB} MB of data into Redis...")
    data = write_data_into_redis(container_id, KEYS_COUNT, BYTES_PER_KEY)
    print(f"Successfully written {DATA_SIZE_MB} MB of data into Redis.")

    # Create a checkpoint
    start_time_checkpoint = time.time()  # Start time for checkpointing
    run_command(
        f"docker checkpoint create --checkpoint-dir={CHECKPOINT_DIR} "
        f"redis {CHECKPOINT_NAME}"
    )
    end_time_checkpoint = time.time()  # End time for checkpointing
    print(f"Checkpoint created at {CHECKPOINT_DIR}/{CHECKPOINT_NAME}.")
    print(
        "Time taken to checkpoint: "
        f"{end_time_checkpoint - start_time_checkpoint:.2f} seconds."
    )

    # Get checkpoint size (uncompressed)
    checkpoint_size_bytes = get_directory_size(
        os.path.join(CHECKPOINT_DIR, CHECKPOINT_NAME)
    )
    print(
        "Size of uncompressed checkpoint: "
        f"{checkpoint_size_bytes / (1024 * 1024):.2f} MB"
    )

    # Create a new container
    clone_container_id = run_command(
        "docker create --name redis-clone --security-opt seccomp:unconfined "
        "redis/redis-stack-server:latest"
    )
    print(f"Cloned container created with ID: {clone_container_id}")

    # Compress and save the checkpoint
    start_time_compress = time.time()  # Start time for compressing
    os.makedirs(os.path.expanduser("~/docker-checkpoints"), exist_ok=True)
    run_command(
        f"sudo tar -czvf ~/docker-checkpoints/{CHECKPOINT_NAME}.tar.gz "
        f"-C {CHECKPOINT_DIR} {CHECKPOINT_NAME}"
    )
    end_time_compress = time.time()  # End time for compressing
    compressed_checkpoint_size_bytes = os.path.getsize(
        os.path.expanduser(f"~/docker-checkpoints/{CHECKPOINT_NAME}.tar.gz")
    )
    print(
        "Size of compressed checkpoint: "
        f"{compressed_checkpoint_size_bytes / (1024 * 1024):.2f} MB"
    )
    print(
        f"Time taken to compress: "
        f"{end_time_compress - start_time_compress:.2f} seconds."
    )

    # Decompress and move the checkpoint to the cloned container
    # This is a workaround, see:
    # https://github.com/moby/moby/issues/37344#issuecomment-450782189
    run_command(
        f"sudo tar -xzvf ~/docker-checkpoints/{CHECKPOINT_NAME}.tar.gz "
        f"-C /var/lib/docker/containers/{clone_container_id}/checkpoints/"
    )
    print("Checkpoint compressed and moved.")

    # Start the new container from the checkpoint
    run_command(f"docker start --checkpoint={CHECKPOINT_NAME} redis-clone")
    print("Cloned container started from checkpoint.")

    # Verify the data in the cloned container
    print("Verifying data in the cloned container...")
    verify_data_in_cloned_container(clone_container_id, data)
    print("All data successfully verified in the cloned container.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(str(e))
