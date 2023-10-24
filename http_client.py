import requests
from config import CHECKPOINT_NAME

from restore import restore


def get_checkpoint_file(container_id):
    url = f"http://192.168.1.2:8000/containers/{container_id}"

    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Save the file
    checkpoint_name = f"{CHECKPOINT_NAME}-{container_id}"
    file_path = f"{checkpoint_name}.tar.gz"
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return file_path


if __name__ == "__main__":
    while True:
        container_name = input("Enter container name (or 'exit' to quit): ")

        if container_name.lower() == "exit":
            break

        try:
            file_path = get_checkpoint_file(container_id=container_name)
            print(f"File saved at {file_path}")
            checkpoint_name = f"{CHECKPOINT_NAME}-{container_name}"
            restore(
                checkpoint_file_path=file_path,
                container_name=container_name,
                checkpoint_name=checkpoint_name,
            )

        except requests.RequestException as e:
            print(
                "Error fetching checkpoint for container "
                f"{container_name}: {e}"
            )
