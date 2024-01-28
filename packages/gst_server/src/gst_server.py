import logging
import sys
import typing
import requests
import time

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    stream=sys.stdout,
)

# CSV Header fields based on json path from podman --print-stats
# Checkpoint stats
CHECKPOINT_STATS_FIELD = "checkpoint_stats"
CHECKPOINT_CONTAINER_STATISTICS_FIELD = (
    f"{CHECKPOINT_STATS_FIELD}.container_statistics"
)
CHECKPOINT_CRIU_STATISTICS_FIELD = (
    f"{CHECKPOINT_CONTAINER_STATISTICS_FIELD}.criu_statistics"
)

# Restore stats
RESTORE_STATS_FIELD = "restore_stats"
RESTORE_CONTAINER_STATISTICS_FIELD = (
    f"{RESTORE_STATS_FIELD}.container_statistics"
)
RESTORE_CRIU_STATISTICS_FIELD = (
    f"{RESTORE_CONTAINER_STATISTICS_FIELD}.criu_statistics"
)

CSV_HEADER = (
    "t,"
    "source_sat,"
    "target_sat,"
    "total_duration,"
    "total_checkpoint_duration,"
    f"{CHECKPOINT_STATS_FIELD}.podman_checkpoint_duration,"
    f"{CHECKPOINT_CONTAINER_STATISTICS_FIELD}"
    f".runtime_checkpoint_duration,"
    f"{CHECKPOINT_CRIU_STATISTICS_FIELD}.freezing_time,"
    f"{CHECKPOINT_CRIU_STATISTICS_FIELD}.frozen_time,"
    f"{CHECKPOINT_CRIU_STATISTICS_FIELD}.memdump_time,"
    f"{CHECKPOINT_CRIU_STATISTICS_FIELD}.memwrite_time,"
    f"{CHECKPOINT_CRIU_STATISTICS_FIELD}.pages_scanned,"
    f"{CHECKPOINT_CRIU_STATISTICS_FIELD}.pages_written,"
    f"{CHECKPOINT_CRIU_STATISTICS_FIELD}.memdump_time,"
    "total_restore_duration,"
    f"{RESTORE_STATS_FIELD}.podman_restore_duration,"
    f"{RESTORE_CONTAINER_STATISTICS_FIELD}"
    f".runtime_restore_duration,"
    f"{RESTORE_CRIU_STATISTICS_FIELD}.forking_time,"
    f"{RESTORE_CRIU_STATISTICS_FIELD}.pages_restored,"
    f"{RESTORE_CRIU_STATISTICS_FIELD}.restore_time\n"
)


def json_to_csv_line(t, source_sat, target_sat, json_data):
    total_checkpoint_duration = json_data.get("checkpoint_duration", "")

    checkpoint_stats = json_data.get("checkpoint_stats", {})
    podman_checkpoint_duration = checkpoint_stats.get(
        "podman_checkpoint_duration", ""
    )

    container_stats = checkpoint_stats.get("container_statistics", [{}])[0]
    runtime_checkpoint_duration = container_stats.get(
        "runtime_checkpoint_duration", ""
    )

    criu_stats = container_stats.get("criu_statistics", {})
    freezing_time = criu_stats.get("freezing_time", "")
    frozen_time = criu_stats.get("frozen_time", "")
    memdump_time = criu_stats.get("memdump_time", "")
    memwrite_time = criu_stats.get("memwrite_time", "")
    pages_scanned = criu_stats.get("pages_scanned", "")
    pages_written = criu_stats.get("pages_written", "")

    total_restore_duration = json_data.get("restore_duration", "")

    restore_stats = json_data.get("restore_stats", {})
    podman_restore_duration = restore_stats.get("podman_restore_duration", "")

    restore_container_stats = restore_stats.get("container_statistics", [{}])[
        0
    ]
    runtime_restore_duration = restore_container_stats.get(
        "runtime_restore_duration", ""
    )

    restore_criu_stats = restore_container_stats.get("criu_statistics", {})
    forking_time = restore_criu_stats.get("forking_time", "")
    pages_restored = restore_criu_stats.get("pages_restored", "")
    restore_time = restore_criu_stats.get("restore_time", "")

    total_duration = float(total_checkpoint_duration) + float(
        total_restore_duration
    )

    # Prepare CSV line as a simple string
    csv_line = (
        f"{t},"
        f"{source_sat},"
        f"{target_sat},"
        f"{total_duration},"
        f"{total_checkpoint_duration},"
        f"{podman_checkpoint_duration},"
        f"{runtime_checkpoint_duration},"
        f"{freezing_time},"
        f"{frozen_time},"
        f"{memdump_time},"
        f"{memwrite_time},"
        f"{pages_scanned},"
        f"{pages_written},"
        f"{memdump_time},"
        f"{total_restore_duration},"
        f"{podman_restore_duration},"
        f"{runtime_restore_duration},"
        f"{forking_time},"
        f"{pages_restored},"
        f"{restore_time}"
    )
    return csv_line


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
        migration_duration_us = (time.time() - migration_start_time) * 1000000

        if response.status_code == 200:
            logging.info(
                f"Migration completed successfully in "
                f"{migration_duration_us:.2f}µs"
                f"({migration_duration_us / 1000000:.2f} s)."
            )
        else:
            logging.error(
                f"Migration failed with status code: {response.status_code}. "
                f"Reason: {response.text}"
            )
            return None

        return response.json()

    except requests.RequestException as e:
        logging.error(f"Error sending migration request to target: {e}")
        return None


# TODO: cleanup
# def stop_container(target_ip, container_id):
#     url = f"http://{target_ip}:8000/stop_container/{container_id}"
#     try:
#         response = requests.post(url)
#         logging.info(f"Response: {response.status_code}, {response.text}")
#     except requests.RequestException as e:
#         logging.error(f"Error: {e}")


# def remove_container(target_ip, container_id):
#     url = f"http://{target_ip}:8000/remove_container/{container_id}"
#     try:
#         response = requests.post(url)
#         logging.info(f"Response: {response.status_code}, {response.text}")
#     except requests.RequestException as e:
#         logging.error(f"Error: {e}")


# def remove_volume(target_ip, volume_id):
#     url = f"http://{target_ip}:8000/remove_volume/{volume_id}"
#     try:
#         response = requests.post(url)
#         logging.info(f"Response: {response.status_code}, {response.text}")
#     except requests.RequestException as e:
#         logging.error(f"Error: {e}")


def notify_client(client_ip, target_ip):
    url = f"http://{client_ip}:8000/notify"
    payload = {"host": target_ip}

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response
        else:
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
        return None


def notify_client_retry(client_ip, target_ip, retries=5):
    for _ in range(retries):
        notify_response = notify_client(client_ip, target_ip)
        if notify_response is None:
            logging.error(f"Failed to notify client of {target_ip}")
            time.sleep(1)
        else:
            break


def build_sat_domain(sat):
    id = sat["sat"]
    shell = sat["shell"]
    return f"{id}.{shell}.celestial"


def test_migration(gateway, period_seconds=5):
    logging.info(f"Starting migration test with {period_seconds=}")
    with open("migration.csv", "w") as f:
        f.write(CSV_HEADER)

        # The sat where the container is currently running
        current_sat = None

        # Keep track of seen sats
        # TODO: add logic to remove old sats
        # TODO: to allow migrations after the first orbit
        seen_sats = {}
        while True:
            time.sleep(period_seconds)

            logging.info(f"{current_sat=}")

            gst = get_gst("berlin", gateway)
            connected_sats = gst["connectedSats"]
            logging.info(f"{connected_sats=}")

            if connected_sats is None or len(connected_sats) == 0:
                logging.warning("No connected sats")
                continue

            # Start container on the first satellite
            if current_sat is None:
                sat = None
                if len(connected_sats) == 1:
                    sat = connected_sats[0]["sat"]
                else:
                    # Choose the one with a larger ID
                    # TODO: choose the one that just entered the bounding box
                    sat = connected_sats[0]["sat"]
                    for connected_sat in connected_sats:
                        if connected_sat["sat"]["sat"] > sat["sat"]:
                            sat = connected_sat["sat"]
                sat_domain = build_sat_domain(sat)
                logging.info(f"First host: {sat_domain}")

                response = start_container(sat_domain, "redis")
                if response is None:
                    logging.error(f"Failed to start redis on {sat_domain=}")
                    continue

                # Update current_sat, seen_sats, and notify client
                sat["domain"] = sat_domain
                seen_sats[sat["sat"]] = sat
                current_sat = sat
                notify_client_retry("client.gst.celestial", sat_domain)
                continue

            # Container is running on current_sat, perform migration
            # TODO: Add logic to not do this periodically, but only when
            # the satellite is about to leave the bounding box
            logging.info(f'Current host: {current_sat["domain"]}')
            next_sat = None
            for connected_sat in connected_sats:
                sat = connected_sat["sat"]
                if sat["sat"] in seen_sats:
                    continue

                sat_domain = build_sat_domain(sat)
                sat["domain"] = sat_domain
                logging.info(f"Next host found: {sat_domain}")
                next_sat = sat
                seen_sats[sat["sat"]] = sat
                break

            if next_sat is None:
                logging.warning("No next host found")
                continue

            logging.info(
                f"Sending migration request to "
                f"{next_sat['domain']}, "
                f"migrating from {current_sat['domain']} "
                f"to {next_sat['domain']}"
            )
            response = send_container_migration_request(
                current_sat["domain"], next_sat["domain"], "redis"
            )
            if response is None:
                logging.error(f"Migration failed for {next_sat}")
                continue

            # Update current_sat and notify client
            current_sat = next_sat
            notify_client_retry("client.gst.celestial", sat_domain)

            # Write migration stats to file
            csv_line = json_to_csv_line(
                time.time(),
                current_sat["sat"],
                next_sat["sat"],
                response,
            )
            f.write(csv_line)
            f.flush()


def main():
    if len(sys.argv) != 2:
        exit(
            "Usage: python3 gst_server.py [gateway] \n   "
            "OR: start-gst-server [gateway]"
        )
    gateway = sys.argv[1]
    logging.info(f"Hello from ground station server! Gateway is {gateway}")

    wait_seconds = 20
    logging.info(f"Waiting {wait_seconds}s for initialization")
    time.sleep(wait_seconds)

    self = get_self(gateway)
    logging.info(f"/self:\n{self}\n")

    info = get_info(gateway)
    logging.info(f"/info:\n{info}\n")

    shell_id = get_shell(0, gateway)
    logging.info(f"/shell/{0}:\n{shell_id}\n")

    # START MIGRATION TEST
    test_migration(gateway=gateway, period_seconds=5)

    # TODO: Cleanup
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


if __name__ == "__main__":
    main()
