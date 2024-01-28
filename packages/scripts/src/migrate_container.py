import json
import sys
import time
import requests

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
        stats = response.json()
        migration_duration_ms = (time.time() - migration_start_time) * 1000
        with open("client.csv", "w", newline="\n", encoding="utf-8") as f:
            f.write(CSV_HEADER)

            if response.status_code == 200:
                print(
                    f"Migration completed successfully in "
                    f"{migration_duration_ms:.2f} ms."
                )
                print(json.dumps(stats, indent=4))
                f.write(
                    json_to_csv_line(
                        t=time.time(),
                        source_sat=source_ip,
                        target_sat=target_ip,
                        json_data=stats,
                    )
                )
            else:
                print(
                    f"Migration failed with status code: {response.status_code}."
                    f"Reason: {response.text}"
                )
    except requests.RequestException as e:
        print(f"Error sending migration request to target: {e}")


def main():
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


if __name__ == "__main__":
    main()
