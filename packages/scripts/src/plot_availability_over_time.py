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

start_migration_changes = (df['status'].shift(1) == 'success') & (df['status'] == 'fail')

# Convert 't_relative' for the points of status change
start_change_points = df.loc[start_migration_changes, 't_relative']

# Identifying indices where status changes from 'fail' to 'success' for end of migration
end_migration_changes = (df['status'].shift(1) == 'fail') & (df['status'] == 'success')

# Convert 't_relative' for the points of end of migration
end_change_points = df.loc[end_migration_changes, 't_relative']

colors = sns.color_palette("deep", n_colors=5)
blue = colors[0]
orange = colors[1]
green = colors[2]
red = colors[3]


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

# Mark the status change points on the x-axis with vertical lines
for cp in start_change_points:
    plt.axvline(x=cp, color=red, linestyle=':', label='Start of migration' if cp == start_change_points.iloc[0] else "")
    
# Mark the end of migration change points on the x-axis with vertical lines
for ecp in end_change_points:
    plt.axvline(x=ecp, color=green, linestyle=':', label='End of migration' if ecp == end_change_points.iloc[0] else "")

plt.legend()

# Display the plot
plt.savefig(
    f"../../fig/plot_availability_{file_name_without_extension}.pdf",
    dpi=1000,
    format="pdf",
)
