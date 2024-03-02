import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import seaborn as sns

sns.set_theme()
# Define colors from Seaborn's palette
colors = sns.color_palette("deep", n_colors=3)

args = sys.argv
if len(args) < 3:
    print(
        "Usage: python plot_average_migration.py <migration-empty.csv> "
        "<migration-100.csv> <migration-500.csv> <migration-1000.csv> "
        "<migration-2500.csv> <migration-5000.csv>\n"
    )
    sys.exit(1)

file_name_0 = args[1]
file_name_100 = args[2]
file_name_500 = args[3]
file_name_1000 = args[4]
file_name_2500 = args[5]
file_name_5000 = args[6]

CHECKPOINT_DURATION = "checkpoint_stats.podman_checkpoint_duration"
RESTORE_DURATION = "restore_stats.podman_restore_duration"

df_0 = pd.read_csv(file_name_0)
df_0["rest_duration"] = (
    df_0["total_duration"] - df_0[CHECKPOINT_DURATION] - df_0[RESTORE_DURATION]
)
mean_c_duration_0 = df_0[CHECKPOINT_DURATION].mean() / 1000000
mean_r_duration_0 = df_0[RESTORE_DURATION].mean() / 1000000
mean_rest_duration_0 = df_0["rest_duration"].mean() / 1000000


df_100 = pd.read_csv(file_name_100)
df_100["rest_duration"] = (
    df_100["total_duration"]
    - df_100[CHECKPOINT_DURATION]
    - df_100[RESTORE_DURATION]
)
mean_c_duration_100 = df_100[CHECKPOINT_DURATION].mean() / 1000000
mean_r_duration_100 = df_100[RESTORE_DURATION].mean() / 1000000
mean_rest_duration_100 = df_100["rest_duration"].mean() / 1000000

df_500 = pd.read_csv(file_name_500)
df_500["rest_duration"] = (
    df_500["total_duration"]
    - df_500[CHECKPOINT_DURATION]
    - df_500[RESTORE_DURATION]
)
mean_c_duration_500 = df_500[CHECKPOINT_DURATION].mean() / 1000000
mean_r_duration_500 = df_500[RESTORE_DURATION].mean() / 1000000
mean_rest_duration_500 = df_500["rest_duration"].mean() / 1000000

df_1000 = pd.read_csv(file_name_1000)
df_1000["rest_duration"] = (
    df_1000["total_duration"]
    - df_1000[CHECKPOINT_DURATION]
    - df_1000[RESTORE_DURATION]
)
mean_c_duration_1000 = df_1000[CHECKPOINT_DURATION].mean() / 1000000
mean_r_duration_1000 = df_1000[RESTORE_DURATION].mean() / 1000000
mean_rest_duration_1000 = df_1000["rest_duration"].mean() / 1000000

df_2500 = pd.read_csv(file_name_2500)
df_2500["rest_duration"] = (
    df_2500["total_duration"]
    - df_2500[CHECKPOINT_DURATION]
    - df_2500[RESTORE_DURATION]
)
mean_c_duration_2500 = df_2500[CHECKPOINT_DURATION].mean() / 1000000
mean_r_duration_2500 = df_2500[RESTORE_DURATION].mean() / 1000000
mean_rest_duration_2500 = df_2500["rest_duration"].mean() / 1000000

df_5000 = pd.read_csv(file_name_5000)
df_5000["rest_duration"] = (
    df_5000["total_duration"]
    - df_5000[CHECKPOINT_DURATION]
    - df_5000[RESTORE_DURATION]
)
mean_c_duration_5000 = df_5000[CHECKPOINT_DURATION].mean() / 1000000
mean_r_duration_5000 = df_5000[RESTORE_DURATION].mean() / 1000000
mean_rest_duration_5000 = df_5000["rest_duration"].mean() / 1000000

# complete here
data = {
    "Instance Size (MB)": ["0", "100", "500", "1000", "2500", "5000"],
    "Checkpoint Duration (s)": [
        mean_c_duration_0,
        mean_c_duration_100,
        mean_c_duration_500,
        mean_c_duration_1000,
        mean_c_duration_2500,
        mean_c_duration_5000,
    ],
    "Restore Duration (s)": [
        mean_r_duration_0,
        mean_r_duration_100,
        mean_r_duration_500,
        mean_r_duration_1000,
        mean_r_duration_2500,
        mean_r_duration_5000,
    ],
    "Rest Duration (s)": [
        mean_rest_duration_0,
        mean_rest_duration_100,
        mean_rest_duration_500,
        mean_rest_duration_1000,
        mean_rest_duration_2500,
        mean_rest_duration_5000,
    ],
}
print(data)
df_plot = pd.DataFrame(data)

plt.figure(figsize=(12, 6))


# Plotting each stack component

plt.bar(
    df_plot["Instance Size (MB)"],
    df_plot["Restore Duration (s)"],
    color=colors[0],
    label="Restore Duration",
)
plt.bar(
    df_plot["Instance Size (MB)"],
    df_plot["Checkpoint Duration (s)"],
    bottom=df_plot["Restore Duration (s)"],
    color=colors[1],
    label="Checkpoint Duration",
)
plt.bar(
    df_plot["Instance Size (MB)"],
    df_plot["Rest Duration (s)"],
    bottom=df_plot["Restore Duration (s)"]
    + df_plot["Checkpoint Duration (s)"],
    color=colors[2],
    label="Rest Duration",
)


# Adding labels and title
plt.xlabel("Instance size (MB)")
plt.ylabel("Mean event duration (s)")
# plt.title("Mean Migration Duration vs Instance Size")
plt.legend()
# Save the plot
plt.savefig(
    "../../fig/avg_migration_durations_components.pdf",
    dpi=1000,
    format="pdf",
)
