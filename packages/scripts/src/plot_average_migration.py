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
        "<migration-2500.csv> <migration-5000.csv>\n"
    )
    sys.exit(1)

file_name_0 = args[1]
file_name_100 = args[2]
file_name_500 = args[3]
file_name_1000 = args[4]
file_name_2500 = args[5]
file_name_5000 = args[6]


df_0 = pd.read_csv(file_name_0)
average_duration_0 = df_0["total_duration"].mean() / 1000000

df_100 = pd.read_csv(file_name_100)
average_duration_100 = df_100["total_duration"].mean() / 1000000

df_500 = pd.read_csv(file_name_500)
average_duration_500 = df_500["total_duration"].mean() / 1000000

df_1000 = pd.read_csv(file_name_1000)
average_duration_1000 = df_1000["total_duration"].mean() / 1000000

df_2500 = pd.read_csv(file_name_2500)
average_duration_2500 = df_2500["total_duration"].mean() / 1000000

df_5000 = pd.read_csv(file_name_5000)
average_duration_5000 = df_5000["total_duration"].mean() / 1000000

data = {
    "Instance Size (MB)": [
        "0 (base image only)",
        "100",
        "500",
        "1000",
        "2500",
        "5000",
    ],
    "Average Migration Duration (seconds)": [
        average_duration_0,
        average_duration_100,
        average_duration_500,
        average_duration_1000,
        average_duration_2500,
        average_duration_5000,
    ],
}
df_plot = pd.DataFrame(data)

# Plotting with Seaborn for consistency
plt.figure(figsize=(12, 5))
sns.set_theme()  # Ensures that the theme is applied
sns.barplot(
    x="Instance Size (MB)",
    y="Average Migration Duration (seconds)",
    data=df_plot,
)

# Adding value labels
for index, row in df_plot.iterrows():
    plt.text(
        index,
        row["Average Migration Duration (seconds)"],
        f"{row['Average Migration Duration (seconds)']:.2f}",
        color="black",
        ha="center",
        va="bottom",
    )

# Axes labels
plt.xlabel("Size of the instance (in MB)")
plt.ylabel("Average migration duration (in seconds)")

# Title
plt.title("Average Migration Duration Per Instance Size")

# Save the plot
plt.savefig(
    "../../fig/avg_migration_durations_seaborn.pdf", dpi=1000, format="pdf"
)
