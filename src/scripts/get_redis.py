import sys
import requests


def get_redis(target_ip, key):
    url = f"http://{target_ip}:8000/get_redis/{key}"
    try:
        response = requests.get(url)
        print(f"Response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Error: {e}")


def main():
    if len(sys.argv) != 3:
        print("Usage: get-redis <target_ip> <key>")
        sys.exit(1)
    target_ip = sys.argv[1]
    key = sys.argv[2]
    get_redis(target_ip, key)


if __name__ == "__main__":
    main()
