import sys
import requests


def remove_volume(target_ip, volume_id):
    url = f"http://{target_ip}:8000/remove_volume/{volume_id}"
    try:
        response = requests.post(url)
        print(f"Response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Error: {e}")


def main():
    if len(sys.argv) != 3:
        print("Usage: remove-volume <target_ip> <volume_id>")
        sys.exit(1)
    target_ip = sys.argv[1]
    volume_id = sys.argv[2]
    remove_volume(target_ip, volume_id)


if __name__ == "__main__":
    main()
