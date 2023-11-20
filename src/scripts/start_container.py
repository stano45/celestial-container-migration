import sys
import requests


def start_container(target_ip, container_name):
    url = f"http://{target_ip}:8000/start_container"
    payload = {"container_name": container_name}
    try:
        response = requests.post(url, json=payload)
        print(f"Response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Error: {e}")


def main():
    if len(sys.argv) != 3:
        print("Usage: start-container <target_ip> <container_name>")
        sys.exit(1)
    target_ip = sys.argv[1]
    container_name = sys.argv[2]
    start_container(target_ip, container_name)


if __name__ == "__main__":
    main()
