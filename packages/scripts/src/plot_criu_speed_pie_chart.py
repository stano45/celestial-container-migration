import matplotlib.pyplot as plt
import pandas as pd
import sys

args = sys.argv
if len(args) < 2:
    print("Please provide the file name as an argument")
    sys.exit(1)

file_name = args[1]
file_name_without_extension = file_name.split("/")[3].split(".")[0]

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
plt.title("Checkpoint Phase Contribution")

# Plot for restore phase
plt.figure(figsize=(8, 8))
plt.pie(
    checkpoint_contributions,
    labels=checkpoint_contributions.index,
    autopct="%1.1f%%",
)
plt.title("Checkpoint Phase Contribution")
plt.savefig(f"checkpoint_phase_{file_name_without_extension}.png")

plt.figure(figsize=(8, 8))
plt.pie(
    restore_contributions,
    labels=restore_contributions.index,
    autopct="%1.1f%%",
)
plt.title("Restore Phase Contribution")
plt.savefig(f"restore_phase_{file_name_without_extension}.png")


plt.figure(figsize=(12, 9))
plt.bar(checkpoint_contributions.index, checkpoint_contributions)
plt.title("Checkpoint Phase Contribution")
plt.ylabel("Duration (ms)")
plt.xticks(rotation=45)
plt.savefig(f"checkpoint_phase_bar_{file_name_without_extension}.png")

# Bar chart for restore phase contribution
plt.figure(figsize=(12, 9))
plt.bar(restore_contributions.index, restore_contributions)
plt.title("Restore Phase Contribution")
plt.ylabel("Duration (ms)")
plt.xticks(rotation=45)
plt.savefig(f"restore_phase_bar_{file_name_without_extension}.png")
