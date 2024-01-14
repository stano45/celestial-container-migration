from checkpoint import checkpoint
from podman_client import PodmanClient
from requests import RequestException
import requests
import logging
import sys
import time

from restore import restore
from utils import get_checkpoint_path, run_command

from flask import (
    Flask,
    request,
    jsonify,
    send_file,
    has_request_context,
    make_response,
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    stream=sys.stdout,
)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.method = request.method
        else:
            record.url = None
            record.method = None
        # Custom formatting to exclude 'None' values
        if record.url is None and record.method is None:
            log_format = (
                "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            )
        else:
            log_format = "[%(asctime)s] %(levelname)s in %(module)s [%(url)s] [%(method)s]: %(message)s"

        formatter = logging.Formatter(log_format)
        return formatter.format(record)


# Custom Formatter
formatter = RequestFormatter(
    "[%(asctime)s] %(levelname)s in %(module)s [%(url)s] [%(method)s]: %(message)s"
)

for handler in logging.getLogger().handlers:
    handler.setFormatter(formatter)

app = Flask(__name__)

podman_client = PodmanClient()


@app.route("/start_migration", methods=["POST"])
def start_migration():
    data = request.json
    server_ip = data.get("server_ip")
    container_name = data.get("container_name")

    try:
        logging.info(f"Fetching container {container_name}...")
        url = f"http://{server_ip}:8000/containers/{container_name}"

        response = requests.get(url, stream=True)
        response.raise_for_status()

        checkpoint_duration_ms = response.headers.get("X-Duration", "Unknown")
        file_path = get_checkpoint_path(container_name)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Checkpoint saved at {file_path}")

        start = time.time()
        restore(container_name=container_name, checkpoint_file_path=file_path)
        restore_duration_ms = (time.time() - start) * 1000

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Migration completed successfully",
                    "checkpoint_duration": checkpoint_duration_ms,
                    "restore_duration": restore_duration_ms,
                }
            ),
            200,
        )
    except RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/containers/<container_id>", methods=["GET"])
def migrate(container_id):
    start_time = time.time()

    logging.info(f"Checkpointing container {container_id}...")
    checkpoint_path = checkpoint(container_id=container_id)
    logging.info(f"Checkpoint created {checkpoint_path}")
    logging.info(f"Returning container {container_id}.")

    duration_ms = (time.time() - start_time) * 1000

    response = make_response(
        send_file(checkpoint_path, mimetype="application/gzip")
    )
    response.headers["X-Duration"] = str(duration_ms)
    return response


@app.route("/start_container", methods=["POST"])
def start_container():
    data = request.json
    container_name = data.get("container_name")

    if not container_name:
        return (
            jsonify(
                {"status": "error", "message": "Container name is required"}
            ),
            400,
        )

    try:
        start = time.time()
        volumes = podman_client.get_volume_ids_of_container(container_name)
        # Remove the volumes created by the container,
        # otherwise we cannot start it again on this machine
        for volume_id in volumes:
            podman_client.remove_volume(volume_id)
        podman_client.stop_and_remove_container(container_name)
        podman_client.run_redis_container(container_name)
        duration_ms = (time.time() - start) * 1000
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Container {container_name} started"
                    " successfully",
                    "duration": duration_ms,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/stop_container/<container_id>", methods=["POST"])
def stop_container(container_id):
    try:
        podman_client.stop_container(container_id)
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Container {container_id}"
                    "stopped successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/remove_container/<container_id>", methods=["POST"])
def remove_container(container_id):
    try:
        podman_client.remove_container(container_id)
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Container {container_id} "
                    "removed successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/remove_volume/<volume_id>", methods=["POST"])
def remove_volume(volume_id):
    try:
        podman_client.remove_volume(volume_id)
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Volume {volume_id} removed successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/set_redis", methods=["POST"])
def set_redis():
    data = request.json
    key = data.get("key")
    value = data.get("value")
    try:
        command = f"podman exec redis redis-cli SET {key} {value}"
        run_command(command)
        return (
            jsonify(
                {"status": "success", "message": f"Set key {key} in Redis"}
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/get_redis/<key>", methods=["GET"])
def get_redis(key):
    try:
        command = f"podman exec redis redis-cli GET {key}"
        value = run_command(command)
        return (
            jsonify({"status": "success", "key": key, "value": value.strip()}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint returning the status of the server.
    """
    return jsonify({"status": "UP", "message": "Service is healthy"}), 200


def main():
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
