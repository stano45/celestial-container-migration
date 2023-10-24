from flask import Flask, send_file

from checkpoint import checkpoint

app = Flask(__name__)


@app.route("/migrate/<container_name>", methods=["GET"])
def migrate(container_name):
    checkpoint_path = checkpoint(
        container_name
    )  # Call the checkpoint function using the provided container_name
    return send_file(
        checkpoint_path, mimetype="application/gzip"
    )  # Send the raw data of the checkpoint file


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
