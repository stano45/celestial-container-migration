import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

sns.set_theme()
args = sys.argv
if len(args) < 3:
    print(
        "Usage: python plot_criu_speed_pie_chart.py <file_name.csv> <plot_title>\n"
    )
    sys.exit(1)

file_name = args[1]
plot_title = args[2]
file_name_without_extension = file_name.split("/")[-1].split(".")[0]

df = pd.read_csv(filepath_or_buffer=file_name)


# Function to extract the last part of the dot path
def get_last_part(column_name):
    return column_name.split(".")[-1]


# Apply this function to each column in the contributions DataFrame
checkpoint_columns = [
    "checkpoint_stats.container_statistics.criu_statistics.freezing_time",
    "checkpoint_stats.container_statistics.criu_statistics.frozen_time",
    "checkpoint_stats.container_statistics.criu_statistics.memdump_time",
    "checkpoint_stats.container_statistics.criu_statistics.memwrite_time",
]

restore_columns = [
    "restore_stats.container_statistics.criu_statistics.forking_time",
    "restore_stats.container_statistics.criu_statistics.restore_time",
]

# Renaming the columns

checkpoint_contributions = (
    (df[checkpoint_columns] / 1000).sum().rename(get_last_part)
)
restore_contributions = (
    (df[restore_columns] / 1000).sum().rename(get_last_part)
)


# Plot for checkpoint phase
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.pie(
    checkpoint_contributions,
    labels=checkpoint_contributions.index,
    autopct="%1.1f%%",
)
# plt.title(f"Checkpoint Phase Contribution ({plot_title})")

# Plot for restore phase
plt.figure(figsize=(8, 8))
plt.pie(
    checkpoint_contributions,
    labels=checkpoint_contributions.index,
    autopct="%1.1f%%",
)
# plt.title(f"Checkpoint Phase Contribution ({plot_title})")
plt.savefig(
    f"../../fig/checkpoint_phase_{file_name_without_extension}.pdf",
    dpi=1000,
    format="pdf",
)

plt.figure(figsize=(8, 8))
plt.pie(
    restore_contributions,
    labels=restore_contributions.index,
    autopct="%1.1f%%",
)
# plt.title("Restore Phase Contribution")
# plt.savefig(f"restore_phase_{file_name_without_extension}.pdf")


# plt.figure(figsize=(12, 9))
# plt.bar(checkpoint_contributions.index, checkpoint_contributions)
# # plt.title(f"Checkpoint Phase Contribution ({plot_title})")
# plt.ylabel("Duration (ms)")
# plt.xticks(rotation=45)
# plt.savefig(
#     f"../../fig/checkpoint_phase_bar_{file_name_without_extension}.pdf",
#     dpi=1000,
#     format="pdf",
# )

# # Bar chart for restore phase contribution
# plt.figure(figsize=(12, 9))
# plt.bar(restore_contributions.index, restore_contributions)
# plt.title("Restore Phase Contribution")
# plt.ylabel("Duration (ms)")
# plt.xticks(rotation=45)
# plt.savefig(f"restore_phase_bar_{file_name_without_extension}.pdf")
