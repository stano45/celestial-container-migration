import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

sns.set_theme()
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


df_0 = pd.read_csv(file_name_0)
average_duration_0 = df_0["total_duration"].mean() / 1000000

df_100 = pd.read_csv(file_name_100)
average_duration_100 = df_100["total_duration"].mean() / 1000000

df_500 = pd.read_csv(file_name_500)
average_duration_500 = df_500["total_duration"].mean() / 1000000

df_1000 = pd.read_csv(file_name_1000)
average_duration_1000 = df_1000["total_duration"].mean() / 1000000

df_1500 = pd.read_csv(file_name_1500)
average_duration_1500 = df_1500["total_duration"].mean() / 1000000

df_2000 = pd.read_csv(file_name_2000)
average_duration_2000 = df_2000["total_duration"].mean() / 1000000

data = {
    "Instance Size (MB)": [
        "0",
        "100",
        "500",
        "1000",
        "1500",
        "2000",
    ],
    "Mean Migration Duration (seconds)": [
        average_duration_0,
        average_duration_100,
        average_duration_500,
        average_duration_1000,
        average_duration_1500,
        average_duration_2000,
    ],
}
df_plot = pd.DataFrame(data)
# Find the maximum value in your data for setting the ylim appropriately
max_duration = df_plot["Mean Migration Duration (seconds)"].max()

# Increase the upper limit by a percentage (e.g., 10%) for padding

# Plotting with Seaborn for consistency
plt.figure(figsize=(12, 5))
sns.set_theme()  # Ensures that the theme is applied
sns.barplot(
    x="Instance Size (MB)",
    y="Mean Migration Duration (seconds)",
    data=df_plot,
)
plt.ylim(
    0, max_duration * 1.1
)  # Adjust 1.1 as needed to increase/decrease padding

# Adding value labels
for index, row in df_plot.iterrows():
    plt.text(
        index,
        row["Mean Migration Duration (seconds)"],
        f"{row['Mean Migration Duration (seconds)']:.2f}",
        color="black",
        ha="center",
        va="bottom",
    )

# Axes labels
plt.xlabel("Instance size (MB)")
plt.ylabel("Mean migration duration (s)")

# Title
# plt.title("Mean Migration Duration vs Instance Size")

# Save the plot
plt.savefig("../../fig/avg_migration_durations.pdf", dpi=1000, format="pdf")
