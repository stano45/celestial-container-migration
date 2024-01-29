import pandas as pd
import matplotlib.pyplot as plt


# Reading the data into a DataFrame
df = pd.read_csv("migration.csv")

print(df.head())

df.reset_index(drop=True, inplace=True)

df["total_duration"] = df["total_duration"] / 1000000
df["total_checkpoint_duration"] = df["total_checkpoint_duration"] / 1000000
df["total_restore_duration"] = df["total_restore_duration"] / 1000000
total_duration = df["total_duration"]
checkpoint_duration = df["total_checkpoint_duration"]
restore_duration = df["total_restore_duration"]

# Plotting the data
plt.figure(figsize=(16, 6))
plt.plot(total_duration, label="Total Duration")
plt.plot(checkpoint_duration, label="Checkpoint Duration")
plt.plot(restore_duration, label="Restore Duration")
plt.xlabel("Timestamp")
plt.ylabel("Duration (in seconds)")
plt.title("Total vs Checkpoint vs Restore Duration Over Time")
plt.legend()
plt.grid(True)
plt.savefig("migration_duration_over_time.png")
