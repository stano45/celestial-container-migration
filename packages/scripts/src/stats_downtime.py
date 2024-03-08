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

# Create a column to identify changes between success and fail.
df_client['status_change'] = df_client['status'].ne(df_client['status'].shift()).cumsum()

# Group by these changes and filter groups where status is fail.
fail_blocks = df_client[df_client['status'] == 'fail'].groupby('status_change')

# Calculate the start and end of each fail block to find durations.
downtime_periods = fail_blocks['t'].agg(['min', 'max'])

# Calculate the duration of each downtime period.
downtime_periods['duration'] = (downtime_periods['max'] - downtime_periods['min']).dt.total_seconds()

# Sum up the durations of all downtime periods to get the total downtime.
total_downtime = downtime_periods['duration'].sum()

# print("Downtime corrected: ", total_downtime)

# df_migration = pd.read_csv(migration_file_name)
# downtime = df_migration["total_duration"].sum() / 1000000
downtime_percent = (total_downtime / total_timespan) * 100

csv_file_path = f"../../data/stats_downtime_{file_name_without_extension}.csv"
with open(csv_file_path, "w") as f:
    f.write(
        "total_timespan_s,total_downtime_s,downtime_percent,uptime_percent,"
        "avg_rq_latency_ms,rq_failure_rate\n"
    )
    f.write(
        f"{total_timespan:.2f},{total_downtime:.2f},{downtime_percent:.2f},"
        f"{100-downtime_percent:.2f},{avg_latency:.2f},{failure_rate:.2f}\n"
    )
