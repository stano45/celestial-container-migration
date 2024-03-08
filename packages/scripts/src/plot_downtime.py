from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns

# Reading the data into a DataFrame
df = pd.read_csv("../../data/stats_downtime_merged.csv")

# Plotting the data
plt.figure(figsize=(12, 5))
sns.set_theme()
# Bar plot
sns.barplot(
    x="instance_size_mb",
    y="downtime_percent",
    data=df,
)

# Show values on top of the bars
for index, row in df.iterrows():
    plt.text(
        row.name,
        row.downtime_percent,
        str(round(row.downtime_percent, 2)) + "%",
        color="black",
        ha="center",
    )


# Axes labels
plt.xlabel("Instance size (MB)")
plt.ylabel("Downtime (%)")

# Title
# plt.title("Downtime vs Instance Size")

plt.ylim([0, 100])
plt.grid(True)
plt.savefig(
    "../../fig/plot_downtime_percent.pdf",
    dpi=1000,
    format="pdf",
)
