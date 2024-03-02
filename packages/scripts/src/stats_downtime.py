import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

# Convert 'status' to numeric values: 1 for 'success', 0 for 'fail'
df_client["status_code"] = df_client["status"].map({"success": 1, "fail": 0})
# Resetting the time to start from 0
df_client["t_relative"] = df_client["t"] - df_client["t"].min()

# Convert 't' to datetime if it's not already
df_client["t"] = pd.to_datetime(df_client["t"], unit="s")
df_client["latency"] = df_client["latency"] * 1000

# Calculate average latency
avg_latency = df_client["latency"].mean()

# Calculate total timespan in milliseconds
total_timespan = (df_client["t"].max() - df_client["t"].min()).total_seconds()

# Calculate total downtime (sum of latencies for 'fail' status)
# downtime = df_client[df_client["status"] == "fail"]["latency"].sum() / 1000
# downtime_percent = (downtime / total_timespan) * 100

# Calculate failure rate
fail_count = df_client[df_client["status"] == "fail"].shape[0]
total_count = df_client.shape[0]
failure_rate = (fail_count / total_count) * 100


df_migration = pd.read_csv(migration_file_name)
downtime = df_migration["total_duration"].sum() / 1000000
downtime_percent = (downtime / total_timespan) * 100

csv_file_path = f"../../fig/stats_downtime_{file_name_without_extension}.csv"
with open(csv_file_path, "w") as f:
    f.write(
        "Total Timespan,Total Downtime,Downtime Percent,Uptime Percent,Avg Request Latency, Request Failure Rate\n"
    )
    f.write(
        f"{total_timespan:.2f} s,{downtime:.2f} s,{downtime_percent:.2f}%,{100-downtime_percent:.2f}%,{avg_latency:.2f} ms,{failure_rate:.2f}%\n"
    )
