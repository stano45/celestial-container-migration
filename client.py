from flask import Flask, request, jsonify
from requests import RequestException
import requests
from config import CHECKPOINT_NAME

from restore import restore

app = Flask(__name__)


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


@app.route("/start_migration", methods=["POST"])
def start_migration():
    data = request.json
    server_ip = data.get("server_ip")
    container_name = data.get("container_name")

    try:
        file_path = get_checkpoint_file(
            host=server_ip, container_id=container_name
        )
        print(f"File saved at {file_path}")
        checkpoint_name = f"{CHECKPOINT_NAME}-{container_name}"
        restore(
            checkpoint_file_path=file_path,
            container_name=container_name,
            checkpoint_name=checkpoint_name,
        )
        return jsonify({"status": "success"}), 200
    except RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
