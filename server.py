from flask import Flask, send_file

from checkpoint import checkpoint

app = Flask(__name__)


@app.route("/containers/<container_id>", methods=["GET"])
def migrate(container_id):
    print(f"Received request to migrate container {container_id}.")
    checkpoint_path = checkpoint(container_id=container_id)
    return send_file(checkpoint_path, mimetype="application/gzip")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
