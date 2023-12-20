import sys
import time
import typing
import requests
from flask import Flask


def get_id(gateway: str) -> str:
    try:
        response = requests.get("http://%s/self" % gateway)
        data = response.json()

        return data["name"]
    except Exception:
        return ""


def get_shell_num(gateway: str) -> int:
    try:
        while True:
            response = requests.get("http://%s/info" % gateway)

            if response.status_code != 200:
                time.sleep(1.0)
                continue

            data = response.json()
            return data["shells"]

    except Exception:
        return 0


def get_active_sats(shells: int, gateway: str) -> typing.List[typing.Dict]:
    try:
        active = []

        for s in range(shells):
            response = requests.get("http://%s/shell/%d" % (gateway, s))
            data = response.json()

            active.extend(data)

        return active
    except Exception as e:
        print(e)
        return []


app = Flask(__name__)


def main():
    if not len(sys.argv) == 2:
        exit(
            "Usage: python3 server.py [gateway] \n   OR: "
            "start-gst-server  [gateway]"
        )
    gateway = sys.argv[1]
    print("Hello from ground station! Gateway is %s" % gateway)
    id = get_id(gateway)

    print("id is %s" % id)

    shells = get_shell_num(gateway)

    print("found %d shells" % shells)
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
