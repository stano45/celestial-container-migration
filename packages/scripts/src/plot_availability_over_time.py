import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

args = sys.argv
if len(args) < 3:
    print(
        "Usage: python plot_availability_over_time.py <file_name.csv> <plot_title>\n"
    )
    sys.exit(1)

file_name = args[1]
plot_title = args[2]
file_name_without_extension = (
    file_name.split("/")[-1].split(".")[0].replace("-", "_")
)

df = pd.read_csv(file_name)

# Convert 'status' to numeric values: 1 for 'success', 0 for 'fail'
df["status_code"] = df["status"].map({"success": 1, "fail": 0})
# Resetting the time to start from 0
df["t_relative"] = df["t"] - df["t"].min()

# Convert 't' to datetime if it's not already
df["t"] = pd.to_datetime(df["t"], unit="s")
df["latency"] = df["latency"] * 1000

# Plotting
plt.figure(figsize=(12, 5))
sns.set_theme()
sns.lineplot(
    data=df, x="t_relative", y="status_code", markers=True, dashes=False
)
# plt.title(f"Service Availability Over Time ({plot_title})")
plt.xlabel("Timestamp (s)")
plt.ylabel("Availability")
plt.yticks([0, 1], ["Down", "Up"])

# Display the plot
plt.savefig(
    f"../../fig/plot_availability_{file_name_without_extension}.pdf",
    dpi=1000,
    format="pdf",
)
