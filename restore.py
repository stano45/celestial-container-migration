import time
from config import (
    CLEANUP_OLD_CONTAINERS,
    CLONE_REDIS_CONTAINER_NAME,
    USED_CONTAINERS,
)
from docker_client import DockerClient

from utils import (
    run_command,
)


def restore(file_path: str):
    # -----------------------------SETUP------------------------------------
    docker_client = DockerClient()

    # Kill and remove any old containers
    if CLEANUP_OLD_CONTAINERS:
        for container_name in USED_CONTAINERS:
            docker_client.remove_container_by_name(container_name)

    # Create a new container
    restore_start_time = time.time()
    cloned_container = docker_client.create_redis_container(
        container_name="celestial-redis",
    )

    # Decompress and move the checkpoint to the cloned container
    # This is a workaround, see:
    # https://github.com/moby/moby/issues/37344#issuecomment-450782189
    run_command(
        f"sudo tar -xzvf ./{file_path} "
        f"-C /var/lib/docker/containers/{cloned_container.id}/checkpoints/"
    )

    # run_command(
    #     f"sudo mv "
    #     f"{CHECKPOINT_DIR}/{CHECKPOINT_NAME} "
    #     f"/var/lib/docker/containers/{cloned_container.id}/"
    #     f"checkpoints/"
    # )

    # Start the new container from the checkpoint
    docker_client.start_redis_container_from_checkpoint(
        container_id=cloned_container.id, checkpoint_name="checkpoint-redis"
    )

    print("Cloned container started from checkpoint.")
    restore_duration = time.time() - restore_start_time
    print(f"Restore time: {restore_duration:.2f} seconds.")

    # Verify the data in the cloned container
    # print("Verifying data in the cloned container...")
    # # Verify the data in the new Redis container
    # with open(RANDOM_DATA_JSON_PATH, "r") as file:
    #     data = json.load(file)
    #     redis_client = RedisClient(
    #         docker_client.get_container_ip(cloned_container.id)
    #     )
    #     redis_client.verify_data(data)
    #     print("All data verified in the cloned container.")
