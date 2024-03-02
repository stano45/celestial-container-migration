import json
import random
import string
import time
import redis
import logging
from tqdm import tqdm

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
            f"podman run "
            f"--name {container_name} "
            f"-d "
            f"-p {host_port}:{container_port} "
            f"{image_name}"
        )

        run_container_duration_ms = (
            time.time() - run_container_start_time
        ) * 1000
        logging.info(
            f"Container {container_name} started with id: {container_id} "
            f"in {run_container_duration_ms:.2f} ms"
        )

        logging.info("Waiting for the container to start...")
        self.wait_for_redis(container_id)

    def wait_for_redis(self, container_id, max_retries=5):
        retries = max_retries
        while retries > 0:
            time.sleep(1)
            try:
                output = run_command(
                    f"podman exec {container_id} redis-cli PING"
                )
                if output is not None and "PONG" in output:
                    logging.info("Container is ready.")
                    break
                else:
                    logging.info("Container is not ready yet.")
            except RuntimeError:
                logging.error("Error pinging the container. Retrying...")
                retries - 1

    def _restore_checkpoint(
        self, checkpoint_path, print_stats=True, retries=3
    ):
        for attempt in range(retries):
            try:
                stats_command = "--print-stats" if print_stats else ""
                stats = run_command(
                    f"podman container restore -i {checkpoint_path} "
                    f"{stats_command} --tcp-established"
                )
                logging.info(
                    f"Container started successfully from path "
                    f"{checkpoint_path} with {stats=}"
                )
                logging.info("Waiting for the container to start...")
                # TODO: use the container id from the stats
                self.wait_for_redis("redis")
                return stats
            except RuntimeError as e:
                logging.error(f"Error restoring checkpoint: {e}")
                if attempt < retries - 1:
                    logging.info(
                        f"Retrying restore... {retries - attempt - 1} "
                        f"attempts left."
                    )
                    time.sleep(1)
                else:
                    logging.error("All retries failed.")
                    return None

    def remove_old_and_restore_container(
        self, old_container_id, checkpoint_path
    ):
        self.stop_and_remove_container(old_container_id)

        restore_start_time = time.time()

        restore_stats = self._restore_checkpoint(
            checkpoint_path=checkpoint_path
        )

        restore_duration_ms = time.time() - restore_start_time
        print(f"Restore time: {restore_duration_ms:.2f} ms")

        return restore_stats

    def _checkpoint_container(
        self, container_id, checkpoint_path, print_stats=True, retries=3
    ):
        stats = None
        for attempt in range(retries):
            try:
                logging.info(
                    f"Checkpointing container {container_id=} to "
                    f"{checkpoint_path=}..."
                )
                stats_command = "--print-stats" if print_stats else ""
                command = (
                    f"podman container checkpoint {container_id} "
                    f"-e={checkpoint_path} {stats_command} --tcp-established"
                )
                stats = run_command(command)
                logging.info(
                    f"Checkpoint created of {container_id=} at "
                    f"{checkpoint_path=} with: {stats=}"
                )
                return stats
            except RuntimeError as e:
                logging.error(f"Error checkpointing container: {e}")
                if attempt < retries - 1:
                    logging.info(
                        f"Retrying checkpointing... {retries - attempt - 1} "
                        f"attempts left."
                    )
                    time.sleep(1)
                else:
                    logging.error("All retries failed.")
                    break
        return stats

    def checkpoint_and_save_container(self, container_id):
        checkpoint_path = get_checkpoint_path(container_id)

        # Get all volumes mounted by the container before checkpointing
        volumes = self.get_volume_ids_of_container(container_id)

        stats = self._checkpoint_container(
            container_id=container_id, checkpoint_path=checkpoint_path
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

        return checkpoint_path, stats

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

    def _write_data(self, redis_client, keys_count, bytes_per_key):
        data = {}
        for i in tqdm(
            range(1, keys_count + 1), desc="Writing data", ncols=100
        ):
            key = f"key{i}"
            value = generate_random_string(bytes_per_key)
            redis_client.set(key, value)
            data[key] = value
        return data

    def generate_redis_data(self, data_size_mb, bytes_per_key):
        logging.info(
            f"Generating {data_size_mb}MB of data with {bytes_per_key} bytes"
            f"per key in Redis..."
        )

        redis_client = redis.Redis(
            host="localhost", port=6379, decode_responses=True
        )

        if redis_client is None:
            logging.error("Redis client is None")

        if redis_client.ping() is False:
            logging.error("Redis client ping failed")

        keys_count = (data_size_mb * 1024 * 1024) // bytes_per_key
        logging.info(
            f"Writing {keys_count} keys with {bytes_per_key} bytes per key"
        )
        self._write_data(
            redis_client=redis_client,
            keys_count=keys_count,
            bytes_per_key=bytes_per_key,
        )

        logging.info(f"Successfully wrote {keys_count} keys")


def generate_random_string(bytes):
    """Generate a random string of given length."""

    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(bytes)
    )
