import json
import time
import logging

from utils import run_command

logger = logging.getLogger(__name__)


class PodmanClient:
    def __init__(self):
        run_command("podman --version")
        logger.info("Podman client initialized.")

    def run_redis_container(
        self,
        container_name,
    ):
        logging.info(f"Running container {container_name}")
        run_container_start_time = time.time()

        container_id = run_command("podman run -d --name redis redis:alpine")

        run_container_duration = (
            time.time() - run_container_start_time
        ) * 1000
        logging.info(
            f"Container {container_name} started with id: {container_id} "
            f"in {run_container_duration:.2f} milliseconds."
        )

    def run_container_from_checkpoint(self, checkpoint_path):
        logging.info(
            f"Starting container " f"from checkpoint {checkpoint_path}..."
        )
        run_command(f"podman container restore -i " f"{checkpoint_path}")

    def create_checkpoint(self, container_id, checkpoint_path):
        logging.info(f"Creating checkpoint {checkpoint_path}...")
        run_command(
            f"podman container checkpoint {container_id} "
            f"-e={checkpoint_path}"
        )

    def stop_container(self, container_id, ignore_error=False):
        logging.info(f"Stopping container {container_id}...")
        run_command(f"podman stop {container_id}", ignore_error=ignore_error)

    def remove_container(self, container_id, ignore_error=False):
        logging.info(f"Removing container {container_id}...")
        run_command(f"podman rm -v {container_id}", ignore_error=ignore_error)

    def stop_and_remove_container(self, container_id):
        self.stop_container(container_id, ignore_error=True)
        self.remove_container(container_id, ignore_error=True)

    # Return container names from podman
    def list_containers(self):
        return run_command("podman ps --format '{{.Names}}'").splitlines()

    def get_volume_ids_of_container(self, container_id):
        logging.info(f"Getting volume IDs of container {container_id}...")
        try:
            # Inspect the container to get its details including volume mounts
            inspect_output = self.inspect_container(container_id)
            container_info = json.loads(inspect_output)

            # Extract volume names from the mount points
            volume_ids = [
                mount["Name"]
                for mount in container_info[0]["Mounts"]
                if mount["Type"] == "volume"
            ]
            return volume_ids
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
        except (KeyError, IndexError) as e:
            logging.error(f"Error extracting volume information: {e}")

        return []

    def remove_volume(self, volume_id):
        logging.info(f"Removing volume {volume_id}...")
        run_command(f"podman volume rm -f {volume_id}", ignore_error=True)

    def inspect_container(self, container_id):
        logging.info(f"Inspecting container {container_id}...")
        return run_command(f"podman inspect {container_id}", ignore_error=True)
