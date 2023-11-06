import json
import os
from src.server.config import (
    RANDOM_DATA_SIZE_MB,
    RANDOM_DATA_KEY_COUNT,
    RANDOM_DATA_JSON_PATH,
    RANDOM_DATA_VOLUME_NAME,
    TEMP_REDIS_CONTAINER_NAME,
)
from scripts.redis_client import RedisClient
from docker_client import DockerClient
from src.server.utils import (
    run_command,
)

RANDOM_DATA_BYTES_PER_KEY = (
    RANDOM_DATA_SIZE_MB * 1024 * 1024
) // RANDOM_DATA_KEY_COUNT


def generate_redis_dump():
    existing_volumes = run_command("docker volume ls -q").split("\n")
    if RANDOM_DATA_VOLUME_NAME not in existing_volumes:
        run_command(f"docker volume create {RANDOM_DATA_VOLUME_NAME}")

    docker_client = DockerClient()

    container = docker_client.run_redis_container(
        volume_name=RANDOM_DATA_VOLUME_NAME,
        container_name=TEMP_REDIS_CONTAINER_NAME,
    )

    redis_client = RedisClient(docker_client.get_container_ip(container.id))
    data = redis_client.write_data(
        RANDOM_DATA_KEY_COUNT, RANDOM_DATA_BYTES_PER_KEY
    )
    redis_client.save()
    # Disable Persistence in Redis
    print("Disabling Redis persistence...")
    run_command(
        f'docker exec {TEMP_REDIS_CONTAINER_NAME} redis-cli config set save ""'
    )
    run_command(
        f"docker exec {TEMP_REDIS_CONTAINER_NAME} redis-cli "
        "config set appendonly no"
    )

    if not os.path.exists("./tmp"):
        os.mkdir("tmp")

    with open(RANDOM_DATA_JSON_PATH, "w") as file:
        json.dump(data, file)

    docker_client.stop_and_remove_container(container.id)

    # print("Waiting 2sec for the container to stop...")
    # time.sleep(2)
