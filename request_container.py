import sys
import time
import requests


def send_container_migration_request(client_ip, server_ip, container_name):
    """Send a request to the client to initiate container migration."""
    client_url = f"http://{client_ip}:9000/start_migration"

    payload = {"server_ip": server_ip, "container_name": container_name}

    try:
        print(
            f"POST Migration request to {client_url}, migrating "
            f"{container_name} from {server_ip} to {client_ip}."
        )
        migration_start_time = time.time()
        response = requests.post(client_url, json=payload)
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
        print(f"Error sending migration request to client: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python script.py <server_ip> <client_ip> <container_name>"
        )
        sys.exit(1)

    server_ip = sys.argv[1]
    client_ip = sys.argv[2]
    container_name = sys.argv[3]

    send_container_migration_request(client_ip, server_ip, container_name)
