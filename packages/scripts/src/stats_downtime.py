import sys
import pandas as pd

args = sys.argv
if len(args) < 3:
    print("Usage: python stats_downtime.py <client.csv> <migration.csv>\n")
    sys.exit(1)

client_file_name = args[1]
migration_file_name = args[2]
file_name_without_extension = (
    client_file_name.split("/")[-1].split(".")[0].replace("-", "_")
)
df_client = pd.read_csv(client_file_name)

df_client["status_code"] = df_client["status"].map({"success": 1, "fail": 0})
df_client["t_relative"] = df_client["t"] - df_client["t"].min()

df_client["t"] = pd.to_datetime(df_client["t"], unit="s")
df_client["latency"] = df_client["latency"] * 1000

avg_latency = df_client["latency"].mean()

total_timespan = (df_client["t"].max() - df_client["t"].min()).total_seconds()

fail_count = df_client[df_client["status"] == "fail"].shape[0]
total_count = df_client.shape[0]
failure_rate = (fail_count / total_count) * 100

df_migration = pd.read_csv(migration_file_name)
downtime = df_migration["total_duration"].sum() / 1000000
downtime_percent = (downtime / total_timespan) * 100

csv_file_path = f"../../data/stats_downtime_{file_name_without_extension}.csv"
with open(csv_file_path, "w") as f:
    f.write(
        "total_timespan_s,total_downtime_s,downtime_percent,uptime_percent,"
        "avg_rq_latency_ms,rq_failure_rate\n"
    )
    f.write(
        f"{total_timespan:.2f},{downtime:.2f},{downtime_percent:.2f},"
        f"{100-downtime_percent:.2f},{avg_latency:.2f},{failure_rate:.2f}\n"
    )
