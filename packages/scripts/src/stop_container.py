import sys
import requests


def stop_container(target_ip, container_id):
    url = f"http://{target_ip}:8000/stop_container/{container_id}"
    try:
        response = requests.post(url)
        print(f"Response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Error: {e}")


def main():
    if len(sys.argv) != 3:
        print("Usage: stop-container <target_ip> <container_id>")
        sys.exit(1)
    target_ip = sys.argv[1]
    container_id = sys.argv[2]
    stop_container(target_ip, container_id)


if __name__ == "__main__":
    main()
