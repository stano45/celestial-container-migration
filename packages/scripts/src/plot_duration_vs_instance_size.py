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
        "<migration-1500.csv> <migration-2000.csv>\n"
    )
    sys.exit(1)

file_name_0 = args[1]
file_name_100 = args[2]
file_name_500 = args[3]
file_name_1000 = args[4]
file_name_1500 = args[5]
file_name_2000 = args[6]

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

df_1500 = pd.read_csv(file_name_1500)
df_1500["rest_duration"] = (
    df_1500["total_duration"]
    - df_1500[CHECKPOINT_DURATION]
    - df_1500[RESTORE_DURATION]
)
mean_c_duration_1500 = df_1500[CHECKPOINT_DURATION].mean() / 1000000
mean_r_duration_1500 = df_1500[RESTORE_DURATION].mean() / 1000000
mean_rest_duration_1500 = df_1500["rest_duration"].mean() / 1000000

df_2000 = pd.read_csv(file_name_2000)
df_2000["rest_duration"] = (
    df_2000["total_duration"]
    - df_2000[CHECKPOINT_DURATION]
    - df_2000[RESTORE_DURATION]
)
mean_c_duration_2000 = df_2000[CHECKPOINT_DURATION].mean() / 1000000
mean_r_duration_2000 = df_2000[RESTORE_DURATION].mean() / 1000000
mean_rest_duration_2000 = df_2000["rest_duration"].mean() / 1000000

# Mean durations for each instance size (mock data based on the structure of the provided code)
# Assuming these are the correct calculations from the user's code
mean_c_durations = np.array(
    [
        mean_c_duration_0,
        mean_c_duration_100,
        mean_c_duration_500,
        mean_c_duration_1000,
        mean_c_duration_1500,
        mean_c_duration_2000,
    ]
)
mean_r_durations = np.array(
    [
        mean_r_duration_0,
        mean_r_duration_100,
        mean_r_duration_500,
        mean_r_duration_1000,
        mean_r_duration_1500,
        mean_r_duration_2000,
    ]
)
mean_rest_durations = np.array(
    [
        mean_rest_duration_0,
        mean_rest_duration_100,
        mean_rest_duration_500,
        mean_rest_duration_1000,
        mean_rest_duration_1500,
        mean_rest_duration_2000,
    ]
)

# Total durations (assuming total_duration is the sum of checkpoint, restore, and rest durations)
mean_total_durations = (
    mean_c_durations + mean_r_durations + mean_rest_durations
)

# Plotting
plt.figure(figsize=(15, 5))
sns.set_theme()
# Define colors from Seaborn's palette
colors = sns.color_palette("deep", n_colors=4)
# Instance sizes
instance_sizes = np.array([0, 100, 500, 1000, 1500, 2000])

# Determine unified y-axis limits based on all durations
all_durations = np.concatenate([mean_total_durations, mean_c_durations, mean_r_durations, mean_rest_durations])
y_min, y_max = all_durations.min(), all_durations.max() * 1.1

# Plot 1: Total Duration vs. Instance Size
plt.figure(figsize=(8, 6))
plt.plot(
    instance_sizes,
    mean_total_durations,
    color=colors[0],
    marker="o",
    linestyle="-",
    linewidth=2,
    markersize=5,
    label="Total Migration Duration",
)
plt.xlabel("Instance size (MB)")
plt.ylabel("Duration (s)")
# plt.title("Total Migration Duration vs. Instance Size")
plt.ylim([y_min, y_max])
plt.grid(True)
plt.legend()
plt.savefig("../../fig/total_migration_duration_vs_instance_size.pdf", dpi=1000, format="pdf")
plt.close()

# Plot 2: Checkpoint Duration vs. Instance Size
plt.figure(figsize=(8, 6))
plt.plot(
    instance_sizes,
    mean_c_durations,
    color=colors[1],
    marker="o",
    linestyle="-",
    linewidth=2,
    markersize=5,
    label="Checkpoint Duration",
)
plt.xlabel("Instance size (MB)")
plt.ylabel("Duration (s)")
# plt.title("Checkpoint Duration vs. Instance Size")
plt.ylim([y_min, y_max])
plt.grid(True)
plt.legend()
plt.savefig("../../fig/checkpoint_duration_vs_instance_size.pdf", dpi=1000, format="pdf")
plt.close()

# Plot 3: Restore Duration vs. Instance Size
plt.figure(figsize=(8, 6))
plt.plot(
    instance_sizes,
    mean_r_durations,
    color=colors[2],
    marker="o",
    linestyle="-",
    linewidth=2,
    markersize=5,
    label="Restore Duration",
)
plt.xlabel("Instance size (MB)")
plt.ylabel("Duration (s)")
# plt.title("Restore Duration vs. Instance Size")
plt.ylim([y_min, y_max])
plt.grid(True)
plt.legend()
plt.savefig("../../fig/restore_duration_vs_instance_size.pdf", dpi=1000, format="pdf")
plt.close()

# Plot 4: Rest Duration vs. Instance Size
plt.figure(figsize=(8, 6))
plt.plot(
    instance_sizes,
    mean_rest_durations,
    color=colors[3],
    marker="o",
    linestyle="-",
    linewidth=2,
    markersize=5,
    label="Rest Duration",
)
plt.xlabel("Instance size (MB)")
plt.ylabel("Duration (s)")
# plt.title("Rest Duration vs. Instance Size")
plt.ylim([y_min, y_max])
plt.grid(True)
plt.legend()
plt.savefig("../../fig/rest_duration_vs_instance_size.pdf", dpi=1000, format="pdf")
plt.close()

# # Plot 1: Total Duration vs. Instance Size
# plt.subplot(1, 3, 1)
# plt.plot(
#     instance_sizes,
#     mean_total_durations,
#     color=colors[0],
#     marker="o",
#     linestyle="-",
#     linewidth=2,
#     markersize=5,
#     label="Total Migration Duration",
# )
# plt.xlabel("Instance size (MB)")
# plt.ylabel("Duration (s)")
# plt.title("Total Migration Duration vs. Instance Size")
# plt.grid(True)
# plt.legend()

# # Plot 2: Checkpoint Duration vs. Instance Size
# plt.subplot(1, 3, 2)
# plt.plot(
#     instance_sizes,
#     mean_c_durations,
#     color=colors[1],
#     marker="o",
#     linestyle="-",
#     linewidth=2,
#     markersize=5,
#     label="Checkpoint Duration",
# )
# plt.xlabel("Instance size (MB)")
# plt.ylabel("Duration (s)")
# plt.title("Checkpoint Duration vs. Instance Size")
# plt.grid(True)
# plt.legend()

# # Plot 3: Restore Duration vs. Instance Size
# plt.subplot(1, 3, 3)
# plt.plot(
#     instance_sizes,
#     mean_r_durations,
#     color=colors[2],
#     marker="o",
#     linestyle="-",
#     linewidth=2,
#     markersize=5,
#     label="Restore Duration",
# )
# plt.xlabel("Instance size (MB)")
# plt.ylabel("Duration (s)")
# plt.title("Restore Duration vs. Instance Size")
# plt.grid(True)
# plt.legend()

# plt.tight_layout()

# # Save the plot
# plt.savefig(
#     "../../fig/avg_duration_vs_instance_size.pdf",
#     dpi=1000,
#     format="pdf",
# )
