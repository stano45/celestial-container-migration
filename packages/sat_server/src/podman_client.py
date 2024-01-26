import json
import time
import logging

from utils import get_checkpoint_path, get_file_size, run_command

logger = logging.getLogger(__name__)


class PodmanClient:
    def __init__(self):
        version = run_command("podman --version")
        logger.info(f"{version}")

    def run_container(
        self,
        container_name="redis",
        image_name="redis:alpine",
        host_port=6379,
        container_port=6379,
    ):
        logging.info(f"Running container {container_name}")
        run_container_start_time = time.time()

        container_id = run_command(
            f"podman run -d --name {container_name} "
            f"-p {host_port}:{container_port} {image_name}"
        )

        run_container_duration = (
            time.time() - run_container_start_time
        ) * 1000
        logging.info(
            f"Container {container_name} started with id: {container_id} "
            f"in {run_container_duration:.2f} milliseconds"
        )

    def __restore_checkpoint(self, checkpoint_path, print_stats=True):
        logging.info(
            f"Starting container from checkpoint {checkpoint_path}..."
        )
        try:
            stats = run_command(
                f"podman container restore "
                f"{'--print-stats' if print_stats is True else ''} "
                f"-i {checkpoint_path}"
            )
        except RuntimeError as e:
            logging.error(f"Error restoring checkpoint: {e}")
        else:
            logging.info(
                f"Container started successfully from path {checkpoint_path} "
                f"with {stats=}"
            )

    def remove_old_and_restore_container(
        self, old_container_id, checkpoint_path
    ):
        self.stop_and_remove_container(old_container_id)

        restore_start_time = time.time()

        self.__restore_checkpoint(checkpoint_path=checkpoint_path)

        restore_duration = time.time() - restore_start_time
        print(f"Restore time: {restore_duration:.2f} seconds")

    def __checkpoint_container(
        self, container_id, checkpoint_path, print_stats=True
    ):
        logging.info(
            f"Checkpointing container {container_id} to {checkpoint_path}..."
        )
        stats = run_command(
            f"podman container checkpoint {container_id} "
            f"-e={checkpoint_path} "
            f"{'--print-stats' if print_stats is True else ''}"
        )
        logging.info(
            f"Checkpoint created of {container_id=} at {checkpoint_path=} "
            f"with: {stats=}"
        )

    def checkpoint_and_save_container(self, container_id):
        checkpoint_path = get_checkpoint_path(container_id)

        # Get all volumes mounted by the container before checkpointing
        volumes = self.get_volume_ids_of_container(container_id)

        checkpoint_start_time = time.time()

        self.__checkpoint_container(
            container_id=container_id, checkpoint_path=checkpoint_path
        )

        checkpoint_duration = time.time() - checkpoint_start_time
        logging.info(
            f"Checkpoint created at {checkpoint_path} "
            f"in {checkpoint_duration:.2f} seconds"
        )

        checkpoint_size_bytes = get_file_size(checkpoint_path)
        logging.info(
            "Size of checkpoint: "
            f"{checkpoint_size_bytes / (1024 * 1024):.2f} MB"
        )

        # The container should not be present after checkpointing
        # but we still try to remove it just in case (ignore errors)
        self.remove_container(container_id)

        # Remove the volumes created by the container,
        # otherwise we cannot start it again on this machine
        for volume_id in volumes:
            self.remove_volume(volume_id)

        return checkpoint_path

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
