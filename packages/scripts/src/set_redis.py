import sys
import requests


def set_redis(target_ip, key, value):
    url = f"http://{target_ip}:8000/set_redis"
    payload = {"key": key, "value": value}
    try:
        response = requests.post(url, json=payload)
        print(f"Response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Error: {e}")


def main():
    if len(sys.argv) != 4:
        print("Usage: set-redis <target_ip> <key> <value>")
        sys.exit(1)
    target_ip = sys.argv[1]
    key = sys.argv[2]
    value = sys.argv[3]
    set_redis(target_ip, key, value)


if __name__ == "__main__":
    main()
