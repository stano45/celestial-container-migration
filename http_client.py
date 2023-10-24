import requests

from restore import restore


def get_checkpoint_file(container_name):
    # Define the URL for the endpoint
    url = f"http://192.168.1.2:8000/migrate/{container_name}"

    # Make the GET request
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Save the file
    file_path = f"{container_name}.tar.gz"
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
            file_path = get_checkpoint_file(container_name)
            print(f"File saved at {file_path}")

            restore(file_path)

        except requests.RequestException as e:
            print(
                "Error fetching checkpoint for container "
                f"{container_name}: {e}"
            )
