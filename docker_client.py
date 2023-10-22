import time
import docker


class DockerClient:
    def __init__(self):
        self.docker_client = docker.DockerClient(
            base_url="unix://var/run/docker.sock"
        )

    def create_volume(self, volume_name):
        print(f"Creating volume {volume_name}...")
        self.docker_client.volumes.create(volume_name)

    def remove_volume(self, volume_name):
        print(f"Removing volume {volume_name}...")
        self.docker_client.volumes.get(volume_name).remove()

    def run_container(
        self,
        image_name,
        volume_name,
        container_name,
    ):
        print(f"Starting container ${container_name}\n")
        run_container_start_time = time.time()

        # Volumes configuration
        volumes = {}
        if volume_name:
            volumes[volume_name] = {"bind": "/data", "mode": "rw"}

        container = self.docker_client.containers.run(
            image_name,
            name=container_name,
            volumes=volumes,
            detach=True,
            security_opt=["seccomp:unconfined"],
            command="--appendonly yes",
        )

        run_container_duration = time.time() - run_container_start_time
        print(
            f"Container ${container_name} started with id: {container.id} "
            f"in {run_container_duration:.2f} seconds."
        )
        print(
            "Waiting 5sec for redis to fully initialize in "
            f"container ${container_name}..."
        )
        time.sleep(5)

        return container

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

    def get_all_redis_containers(self):
        print("ALL CONTAINERS: ", self.list_containers())
        print(
            "redis CONTAINERS: ",
            [
                container
                for container in self.list_containers()
                if "redis" in container.name
            ],
        )
        return [
            container
            for container in self.list_containers()
            if "redis" in container.name
        ]

    def remove_all_redis_containers(self):
        for container in self.get_all_redis_containers():
            self.stop_and_remove_container(container.id)
            print(
                f"Successfully killed and removed container "
                f'"{container.name}".'
            )

    def check_appendonlydir_exist_in_volume(self, volume_name):
        self.docker_client.containers.run(
            "alpine:latest",
            name="temp_check_container",
            volumes={volume_name: {"bind": "/data", "mode": "rw"}},
            detach=True,
            command="tail -f /dev/null",
        )
        time.sleep(2)  # wait for container to be up
        result = self.docker_client.containers.get(
            "temp_check_container"
        ).exec_run("ls /data/appendonlydir")
        self.stop_and_remove_container("temp_check_container")
        return "appendonly.aof.1.incr.aof" in result.output.decode("utf-8")

    # def does_appendonlydir_exist_in_volume(volume_name):
    #     run_command(
    #         "docker run -d --rm "
    #         "--name temp_check_container "
    #         f"-v {volume_name}:/data "
    #         "alpine:latest "
    #         "tail -f /dev/null"
    #     )
    #     time.sleep(2)  # wait for container to be up
    #     result = run_command(
    #         "docker exec temp_check_container ls /data/appendonlydir",
    #         ignore_error=True,
    #     )
    #     run_command("docker stop temp_check_container")
    #     return "appendonly.aof.1.incr.aof" in result
