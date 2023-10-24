import time
import docker
from config import TEMP_CHECK_CONTAINER_NAME

from utils import run_command


class DockerClient:
    def __init__(self):
        self.docker_client = docker.from_env()

    def create_volume(self, volume_name):
        print(f"Creating volume {volume_name}...")
        self.docker_client.volumes.create(volume_name)

    def remove_volume(self, volume_name):
        print(f"Removing volume {volume_name}...")
        self.docker_client.volumes.get(volume_name).remove()

    def run_redis_container(
        self,
        volume_name,
        container_name,
    ):
        print(f"Running container {container_name}")
        run_container_start_time = time.time()

        volumes = {}
        if volume_name:
            volumes[volume_name] = {"bind": "/data", "mode": "rw"}

        container = self.docker_client.containers.run(
            image="redis:latest",
            name=container_name,
            volumes=volumes,
            detach=True,
            security_opt=["seccomp:unconfined"],
            command="--appendonly yes",
        )

        run_container_duration = time.time() - run_container_start_time
        print(
            f"Container {container_name} started with id: {container.id} "
            f"in {run_container_duration:.2f} seconds."
        )
        # print(
        #     "Waiting 2 seconds for redis to initialize in "
        #     f"container {container_name}..."
        # )
        # time.sleep(2)

        return container

    def create_redis_container(self, container_name, volume_name=None):
        print(f"Creating container {container_name}")
        run_container_start_time = time.time()

        volumes = {}
        if volume_name:
            volumes[volume_name] = {"bind": "/data", "mode": "rw"}

        container = self.docker_client.containers.create(
            image="redis:latest",
            name=container_name,
            volumes=volumes,
            detach=True,
            security_opt=["seccomp:unconfined"],
            command="--appendonly yes",
        )

        run_container_duration = time.time() - run_container_start_time
        print(
            f"Container {container_name} created with id: {container.id} "
            f"in {run_container_duration:.2f} seconds."
        )
        return container

    def start_redis_container_from_checkpoint(
        self, container_id, checkpoint_name=None
    ):
        print(
            f"Starting container {container_id} "
            f"from checkpoint {checkpoint_name}..."
        )
        run_command(
            f"docker start --checkpoint={checkpoint_name} {container_id}"
        )

    def create_checkpoint(
        self, container_name, checkpoint_dir, checkpoint_name
    ):
        print(f"Creating checkpoint {checkpoint_name}...")
        run_command(
            "docker checkpoint create "
            f"--checkpoint-dir={checkpoint_dir} "
            f"{container_name} {checkpoint_name}"
        )

    def stop_container(self, container_id):
        print(f"Stopping container {container_id}...")
        self.docker_client.containers.get(container_id).stop()

    def remove_container(self, container_id):
        print(f"Removing container {container_id}...")
        self.docker_client.containers.get(container_id).remove()

    def stop_and_remove_container(self, container_id):
        self.stop_container(container_id)
        self.remove_container(container_id)

    def get_container_ip(self, container_id):
        container_info = self.docker_client.containers.get(container_id).attrs
        return container_info["NetworkSettings"]["IPAddress"]

    def list_containers(self):
        return self.docker_client.containers.list()

    def get_container_by_name(self, container_name):
        return self.docker_client.containers.get(container_name)

    def remove_container_by_name(self, container_name):
        try:
            container = self.docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            print(f"Container {container_name} not found for removing.")
            return

        container.stop()
        container.remove()
        print(
            f"Stopped and removed container {container_name} with ID "
            f'"{container.id}".'
        )

    def remove_all_redis_containers(self):
        containers = self.docker_client.containers.list(all=True)
        for container in containers:
            if "redis" in container.image.tags[0]:
                container.stop()
                container.remove()
                print(
                    f"Stopped and removed container with ID "
                    f'"{container.id}" based on "redis" image.'
                )

    def check_appendonlydir_exist_in_volume(self, volume_name):
        self.docker_client.containers.run(
            "alpine:latest",
            name=TEMP_CHECK_CONTAINER_NAME,
            volumes={volume_name: {"bind": "/data", "mode": "rw"}},
            detach=True,
            command="tail -f /dev/null",
        )
        # time.sleep(2)
        result = self.docker_client.containers.get(
            TEMP_CHECK_CONTAINER_NAME
        ).exec_run("ls /data/appendonlydir")
        self.stop_and_remove_container(TEMP_CHECK_CONTAINER_NAME)
        return "appendonly.aof" in result.output.decode("utf-8")
