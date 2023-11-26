from checkpoint import checkpoint
from podman_client import PodmanClient
from flask import Flask, request, jsonify, send_file
from requests import RequestException
import requests

from restore import restore
from utils import get_checkpoint_path, run_command

app = Flask(__name__)


@app.route("/start_migration", methods=["POST"])
def start_migration():
    data = request.json
    server_ip = data.get("server_ip")
    container_name = data.get("container_name")

    try:
        print(f"Fetching container {container_name}...")
        url = f"http://{server_ip}:8000/containers/{container_name}"

        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save the file
        file_path = get_checkpoint_path(container_name)
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Checkpoint saved at {file_path}")
        restore(container_name=container_name, checkpoint_file_path=file_path)
        return jsonify({"status": "success"}), 200
    except RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/containers/<container_id>", methods=["GET"])
def migrate(container_id):
    print(f"Checkpointing container {container_id}...")
    checkpoint_path = checkpoint(container_id=container_id)
    print(f"Checkpoint created {checkpoint_path}")
    print(f"Returning container {container_id}.")
    return send_file(checkpoint_path, mimetype="application/gzip")


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

    podman_client = PodmanClient()
    try:
        volumes = podman_client.get_volume_ids_of_container(container_name)
        # Remove the volumes created by the container,
        # otherwise we cannot start it again on this machine
        for volume_id in volumes:
            podman_client.remove_volume(volume_id)
        podman_client.stop_and_remove_container(container_name)
        podman_client.run_redis_container(container_name)
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Container {container_name} started"
                    " successfully",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/stop_container/<container_id>", methods=["POST"])
def stop_container(container_id):
    podman_client = PodmanClient()
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
    podman_client = PodmanClient()
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
    podman_client = PodmanClient()
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
