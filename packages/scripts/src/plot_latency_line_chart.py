import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv("client.csv")

# Convert 't' to datetime if it's not already
df["t"] = pd.to_datetime(df["t"], unit="s")
df["latency"] = df["latency"] * 1000

# Calculate average latency
avg_latency = df["latency"].mean()
print(f"Average Latency: {avg_latency:.2f} ms")

# Calculate total timespan in milliseconds
total_timespan = (df["t"].max() - df["t"].min()).total_seconds() * 1000
print(
    f"Total Timespan: {total_timespan:.2f} ms "
    f"({total_timespan / 1000:.2f} seconds)"
)

# Calculate total downtime (sum of latencies for 'fail' status)
downtime = df[df["status"] == "fail"]["latency"].sum()
downtime_percent = (downtime / total_timespan) * 100
print(f"Total Downtime: {downtime:.2f} ms ({downtime_percent:.2f}%)")

# Calculate failure rate
fail_count = df[df["status"] == "fail"].shape[0]
total_count = df.shape[0]
failure_rate = (fail_count / total_count) * 100
print(f"Failure Rate: {failure_rate:.2f}% ({fail_count}/{total_count})")


# Plot
plt.figure(figsize=(10, 6))
plt.plot(df["t"], df["latency"])
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
# plt.yscale("log")
plt.title("Latency Over Time")
plt.savefig("latency_over_time.png")
