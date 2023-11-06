from server.checkpoint import checkpoint
from flask import Flask, request, jsonify, send_file
from requests import RequestException
import requests
from server.config import CHECKPOINT_NAME

from server.restore import restore

app = Flask(__name__)


@app.route("/start_migration", methods=["POST"])
def start_migration():
    data = request.json
    server_ip = data.get("server_ip")
    container_name = data.get("container_name")

    try:
        print(f"Fetching container {container_name}...")

        file_path = get_checkpoint_file(
            host=server_ip, container_id=container_name
        )
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


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint returning the status of the server.
    """
    return jsonify({"status": "UP", "message": "Service is healthy"}), 200


def get_checkpoint_file(host, container_id):
    url = f"http://{host}:8000/containers/{container_id}"

    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Save the file
    checkpoint_name = f"{CHECKPOINT_NAME}-{container_id}"
    file_path = f"{checkpoint_name}.tar.gz"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return file_path


def main():
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
