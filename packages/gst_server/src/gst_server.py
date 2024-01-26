import logging
import sys
import typing
import requests
import time
from flask import Flask, request, has_request_context

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    stream=sys.stdout,
)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.method = request.method
        else:
            record.url = None
            record.method = None
        # Custom formatting to exclude 'None' values
        if record.url is None and record.method is None:
            log_format = (
                "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            )
        else:
            log_format = (
                "[%(asctime)s] %(levelname)s in %(module)s "
                "[%(url)s] [%(method)s]: %(message)s"
            )

        formatter = logging.Formatter(log_format)
        return formatter.format(record)


# Custom Formatter
formatter = RequestFormatter(
    "[%(asctime)s] %(levelname)s in %(module)s "
    "[%(url)s] [%(method)s]: %(message)s"
)

for handler in logging.getLogger().handlers:
    handler.setFormatter(formatter)

app = Flask(__name__)


def get_self(gateway: str) -> str:
    try:
        response = requests.get(f"http://{gateway}/self")
        return response.json()
    except Exception:
        return ""


def get_info(gateway: str):
    try:
        response = requests.get(f"http://{gateway}/info")
        if response.status_code == 200:
            return response.json()
        else:
            return 0
    except Exception as e:
        logging.error(e)
        return 0


def get_shell(shell: int, gateway: str) -> typing.List[typing.Dict]:
    active = []
    try:
        response = requests.get(f"http://{gateway}/shell/{shell}")
        return response.json()
    except Exception as e:
        logging.error(e)
    return active


def get_gst(name: str, gateway: str):
    try:
        response = requests.get(f"http://{gateway}/gst/{name}")
        return response.json()
    except Exception as e:
        logging.error(e)


def get_sat(shell: int, sat: int, gateway: str):
    try:
        response = requests.get(f"http://{gateway}/shell/{shell}/{sat}")
        return response.json()
    except Exception as e:
        logging.error(e)


def get_path(source_shell, source_sat, target_shell, target_sat, gateway: str):
    try:
        response = requests.get(
            f"http://{gateway}/path/{source_shell}"
            f"/{source_sat}/{target_shell}/{target_sat}"
        )
        return response.json()
    except Exception as e:
        logging.error(e)


def start_container(target_ip, container_name):
    url = f"http://{target_ip}:8000/start_container"
    payload = {"container_name": container_name}
    try:
        response = requests.post(url, json=payload)
        logging.info(f"Response: {response.status_code}, {response.text}")
        return response.text
    except requests.RequestException as e:
        logging.error(
            f"Error starting container {container_name} on {target_ip}: {e}"
        )
        return None


def send_container_migration_request(source_ip, target_ip, container_name):
    """Send a request to the client to initiate container migration."""
    target_url = f"http://{target_ip}:8000/start_migration"

    payload = {"server_ip": source_ip, "container_name": container_name}

    try:
        logging.info(
            f"POST Migration request to {target_url}, migrating "
            f"{container_name} from {source_ip} to {target_ip}."
        )
        migration_start_time = time.time()
        response = requests.post(target_url, json=payload)
        migration_duration_ms = (time.time() - migration_start_time) * 1000

        if response.status_code == 200:
            logging.info(
                f"Migration completed successfully in "
                f"{migration_duration_ms:.2f} ms."
            )
        else:
            logging.error(
                f"Migration failed with status code: {response.status_code}. "
                f"Reason: {response.text}"
            )
            return None

        checkpoint_duration_ms = response.json()["checkpoint_duration"]
        restore_duration_ms = response.json()["restore_duration"]
        return (
            migration_duration_ms,
            checkpoint_duration_ms,
            restore_duration_ms,
        )

    except requests.RequestException as e:
        logging.error(f"Error sending migration request to target: {e}")


def stop_container(target_ip, container_id):
    url = f"http://{target_ip}:8000/stop_container/{container_id}"
    try:
        response = requests.post(url)
        logging.info(f"Response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        logging.error(f"Error: {e}")


def remove_container(target_ip, container_id):
    url = f"http://{target_ip}:8000/remove_container/{container_id}"
    try:
        response = requests.post(url)
        logging.info(f"Response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        logging.error(f"Error: {e}")


def remove_volume(target_ip, volume_id):
    url = f"http://{target_ip}:8000/remove_volume/{volume_id}"
    try:
        response = requests.post(url)
        logging.info(f"Response: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        logging.error(f"Error: {e}")


def build_sat_domain(sat):
    id = sat["sat"]
    shell = sat["shell"]
    return f"{id}.{shell}.celestial"


def main():
    if len(sys.argv) != 2:
        exit(
            "Usage: python3 gst_server.py [gateway] \n   "
            "OR: start-gst-server [gateway]"
        )
    gateway = sys.argv[1]
    logging.info(f"Hello from ground station server! Gateway is {gateway}")

    wait_seconds = 20
    logging.info(f"Waiting {wait_seconds} seconds for initialization")
    time.sleep(wait_seconds)

    self = get_self(gateway)
    logging.info(f"/self:\n{self}\n")

    info = get_info(gateway)
    logging.info(f"/info:\n{info}\n")

    shell_id = get_shell(0, gateway)
    logging.info(f"/shell/{0}:\n{shell_id}\n")

    with open("migration.csv", "w") as f:
        f.write(
            "t,"
            "source_sat,"
            "target_sat,"
            "total_duration,"
            "checkpoint_duration,"
            "restore_duration\n"
        )

        current_sat = None
        seen_sats = {}
        while True:
            time.sleep(5)

            gst = get_gst("berlin", gateway)
            # logging.info(f"/gst/berlin:\n{gst}\n")
            connected_sats = gst["connectedSats"]
            logging.info(f"Connected sats: {connected_sats}")

            # for connected_sat in connected_sats:
            #     logging.info(f"Connected sat: {connected_sat}")
            #     sat_id = connected_sat["sat"]
            #     shell_id = sat_id["shell"]
            #     sat_id = sat_id["sat"]
            #     sat_info = get_sat(shell_id, sat_id, gateway)
            #     logging.info(f"/sat/{sat_id}:\n{sat_info}\n")

            #     path = get_path("gst", "berlin", shell_id, sat_id, gateway)
            #     logging.info(f"/path/gst/berlin/{shell_id}/{sat_id}:\n{path}\n")

            #     sat_domain = build_sat_domain(shell_id, sat_id)
            #     logging.info(f"Pinging {sat_domain}")
            #     sat_ping = ping3.ping(sat_domain, unit="ms")
            #     logging.info(f"Ping to {sat_domain}: {sat_ping}")

            if connected_sats is not None and connected_sats != []:
                if current_sat is None:
                    sat = None
                    if len(connected_sats) == 1:
                        sat = connected_sats[0]["sat"]
                    else:
                        # Choose the one with a larger ID
                        sat = connected_sats[0]["sat"]
                        for connected_sat in connected_sats:
                            if connected_sat["sat"]["sat"] > sat["sat"]:
                                sat = connected_sat["sat"]
                    sat_domain = build_sat_domain(sat)
                    logging.info(f"First host: {sat_domain}")
                    response = start_container(sat_domain, "redis")
                    if response is None:
                        logging.error(f"Failed to start redis on {sat_domain}")
                        continue
                    sat["domain"] = sat_domain
                    seen_sats[sat["sat"]] = sat
                    current_sat = sat
                else:
                    logging.info(f'Current host: {current_sat["domain"]}')
                    next_sat = None
                    for connected_sat in connected_sats:
                        sat = connected_sat["sat"]
                        sat_domain = build_sat_domain(sat)
                        sat["domain"] = sat_domain

                        if sat["sat"] not in seen_sats:
                            logging.info(f"Next host: {sat_domain}")
                            next_sat = sat
                            seen_sats[sat["sat"]] = sat
                            break

                    if next_sat is not None:
                        logging.info(
                            f"Sending migration request to "
                            f"{next_sat['domain']}"
                        )
                        response = send_container_migration_request(
                            current_sat["domain"], next_sat["domain"], "redis"
                        )
                        if response is None:
                            logging.error(f"Migration failed for {next_sat}")
                            continue
                        (
                            migration_duration_ms,
                            checkpoint_duration_ms,
                            restore_duration_ms,
                        ) = response
                        if migration_duration_ms is None:
                            logging.error(f"Migration failed for {next_sat}")
                            continue
                        f.write(
                            f"{time.time()},"
                            f"{current_sat['sat']},"
                            f"{next_sat['sat']},"
                            f"{migration_duration_ms},"
                            f"{checkpoint_duration_ms},"
                            f"{restore_duration_ms}\n"
                        )
                        f.flush()

                        current_sat = next_sat
                    else:
                        logging.warning("No next host found")
            else:
                logging.warning("No connected sats")

            # for i in range(25):
            #     sat = get_sat(0, i, gateway)
            #     logging.info(f"/shell/{0}/{i}:\n{sat}\n")

            # for i in range(0, 5):
            #     for j in range(0, 5):
            #         path = get_path(0, i, 0, j, gateway)
            #         if path:
            #             logging.info(f"/path/{0}/{i}/{0}/{j}:\n{path}\n")

            # for i in range(0, 5):
            #     path = get_path("gst", "berlin", 0, i, gateway)
            #     if path:
            #         logging.info(f"/path/gst/berlin/{0}/{i}:\n{path}\n")

    # app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
