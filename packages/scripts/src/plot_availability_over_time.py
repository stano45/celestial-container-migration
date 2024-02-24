import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

args = sys.argv
if len(args) < 2:
    print("Please provide the file name as an argument")
    sys.exit(1)

file_name = args[1]
file_name_without_extension = (
    file_name.split("/")[-1].split(".")[0].replace("-", "_")
)

df = pd.read_csv(file_name)

# Convert 'status' to numeric values: 1 for 'success', 0 for 'fail'
df['status_code'] = df['status'].map({'success': 1, 'fail': 0})
# Resetting the time to start from 0
df['t_relative'] = df['t'] - df['t'].min()

# Convert 't' to datetime if it's not already
df["t"] = pd.to_datetime(df["t"], unit="s")
df["latency"] = df["latency"] * 1000

# Plotting
plt.figure(figsize=(12, 4))
sns.lineplot(data=df, x='t_relative', y='status_code', markers=True, dashes=False)
plt.title('Service availability over time (100 MB instance)')
plt.xlabel('Relative timestamp (seconds)')
plt.ylabel('Availability')
plt.yticks([0, 1], ['Down', 'Up'])

# Display the plot
plt.savefig(f'plot_availability_{file_name_without_extension}.png', dpi=1000)

# Calculate average latency
avg_latency = df["latency"].mean()

# Calculate total timespan in milliseconds
total_timespan = (df["t"].max() - df["t"].min()).total_seconds()

# Calculate total downtime (sum of latencies for 'fail' status)
downtime = df[df["status"] == "fail"]["latency"].sum() / 1000
downtime_percent = (downtime / total_timespan) * 100

# Calculate failure rate
fail_count = df[df["status"] == "fail"].shape[0]
total_count = df.shape[0]
failure_rate = (fail_count / total_count) * 100

csv_file_path = f"stats_availability_{file_name_without_extension}.csv"
with open(csv_file_path, "w") as f:
    f.write("Total Timespan,Total Downtime,Downtime Percent,Uptime Percent,Avg Request Latency, Request Failure Rate\n")
    f.write(f"{total_timespan:.2f} s,{downtime:.2f} s,{downtime_percent:.2f}%,{100-downtime_percent:.2f}%,{avg_latency:.2f} ms,{failure_rate:.2f}%\n")

# Save to CSV

# metrics_values = [
#     ["Average Latency", f"{avg_latency:.2f} ms"],
#     ["Total Timespan", f"{total_timespan:.2f} ms ({total_timespan / 1000:.2f} seconds)"],
#     ["Total Downtime", f"{downtime:.2f} ms ({downtime_percent:.2f}%)"],
#     ["Failure Rate", f"{failure_rate:.2f}% ({fail_count}/{total_count})"]
# ]

# # Convert to DataFrame
# simple_stats_df = pd.DataFrame(metrics_values, columns=["Metric", "Value"])

# # Save to CSV in a simpler format
# simple_csv_file_path = f"simple_stats_availability_{file_name_without_extension}.csv"
# simple_stats_df.to_csv(simple_csv_file_path, index=False, header=False)