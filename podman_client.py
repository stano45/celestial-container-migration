import time

from utils import run_command


class PodmanClient:
    def __init__(self):
        run_command("podman --version")

    def run_redis_container(
        self,
        container_name,
    ):
        print(f"Running container {container_name}")
        run_container_start_time = time.time()

        container_id = run_command(
            "podman run -d --image-volume tmpfs --name redis redis"
        )

        run_container_duration = time.time() - run_container_start_time
        print(
            f"Container {container_name} started with id: {container_id} "
            f"in {run_container_duration:.2f} seconds."
        )

    def run_container_from_checkpoint(self, checkpoint_path):
        print(f"Starting container " f"from checkpoint {checkpoint_path}...")
        run_command(f"podman container restore -i {checkpoint_path}")

    def create_checkpoint(self, container_id, checkpoint_path):
        print(f"Creating checkpoint {checkpoint_path}...")
        run_command(
            f"podman container checkpoint {container_id} "
            f"-e={checkpoint_path} "
        )

    def stop_container(self, container_id, ignore_error=False):
        print(f"Stopping container {container_id}...")
        run_command(f"podman stop {container_id}", ignore_error=ignore_error)

    def remove_container(self, container_id, ignore_error=False):
        print(f"Removing container {container_id}...")
        run_command(f"podman rm {container_id}", ignore_error=ignore_error)

    def stop_and_remove_container(self, container_id):
        self.stop_container(container_id, ignore_error=True)
        self.remove_container(container_id, ignore_error=True)

    # Return container names from podman
    def list_containers(self):
        return run_command("podman ps --format '{{.Names}}'").splitlines()
