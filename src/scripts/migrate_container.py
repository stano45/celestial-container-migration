import sys
import time
import requests


def send_container_migration_request(source_ip, target_ip, container_name):
    """Send a request to the client to initiate container migration."""
    target_url = f"http://{target_ip}:8000/start_migration"

    payload = {"server_ip": source_ip, "container_name": container_name}

    try:
        print(
            f"POST Migration request to {target_url}, migrating "
            f"{container_name} from {source_ip} to {target_ip}."
        )
        migration_start_time = time.time()
        response = requests.post(target_url, json=payload)
        migration_duration = time.time() - migration_start_time
        if response.status_code == 200:
            print(
                f"Migration completed successfully in "
                f"{migration_duration:.2f} seconds."
            )
        else:
            print(
                f"Migration failed with status code: {response.status_code}. "
                f"Reason: {response.text}"
            )
    except requests.RequestException as e:
        print(f"Error sending migration request to target: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python request_container.py "
            "<source_ip> <target_ip> <container_name>"
        )
        sys.exit(1)

    source_ip = sys.argv[1]
    target_ip = sys.argv[2]
    container_name = sys.argv[3]

    send_container_migration_request(source_ip, target_ip, container_name)
