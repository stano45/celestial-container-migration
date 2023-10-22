import json
import os
import time
from redis_client import RedisClient
from docker_client import DockerClient
from utils import (
    DATA_JSON_PATH,
    run_command,
    stop_container,
)

DATA_SIZE_MB = 10
KEYS_COUNT = 100
BYTES_PER_KEY = (DATA_SIZE_MB * 1024 * 1024) // KEYS_COUNT


def get_container_ip(container_id):
    ip = run_command(
        f"docker inspect {container_id} -f "
        f"'{{{{.NetworkSettings.IPAddress}}}}'"
    )
    print(
        f"docker inspect {container_id} -f "
        f"'{{{{.NetworkSettings.IPAddress}}}}'"
    )
    return ip.strip()


# Main function
def generate_redis_dump():
    VOLUME_NAME = "redis_data_volume"

    # Create a named volume if it doesn't exist
    existing_volumes = run_command("docker volume ls -q").split("\n")
    if VOLUME_NAME not in existing_volumes:
        run_command(f"docker volume create {VOLUME_NAME}")

    # Now, start the Redis container with the volume attached
    container_id = run_command(
        "docker run -d "
        "--name redis-tmp-volume "
        "--security-opt seccomp:unconfined "
        f"-v {VOLUME_NAME}:/data "
        "redis:latest "
        "--appendonly yes"
    )

    # Write data into Redis
    redis_ip = get_container_ip(container_id)
    redis_client = RedisClient(redis_ip)
    data = redis_client.write_data(KEYS_COUNT, BYTES_PER_KEY)

    if not os.path.exists("./tmp"):
        os.mkdir("tmp")

    # Save the data to a JSON file in the current directory
    with open(DATA_JSON_PATH, "w") as file:
        json.dump(data, file)

    # Kill and remove the old containerded from append only file: 0.009 seconds
    stop_container(container_id)

    # Wait for the container to stop
    print("Waiting 5sec for the container to stop...")
    time.sleep(5)
