
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


args = sys.argv
if len(args) < 2:
    print(
        "Usage: python client_latency_scatter.py <file_name>\n"
    )
    sys.exit(1)

file_name = args[1]
file_name = args[1]
file_name_without_extension = (
    file_name.split("/")[-1].split(".")[0].replace("-", "_")
)
# Reading the CSV data back in from the file
df = pd.read_csv(file_name)

# Filtering for success status
df["latency"] = df["latency"] * 1000
df["t_relative"] = df["t"] - df["t"].min()

# Convert 't' to datetime if it's not already
df["t"] = pd.to_datetime(df["t"], unit="s")
df_success = df[df['status'] == 'success'].copy()
window_size = 5  # Adjust based on your preference
df_success['latency_ma'] = df_success['latency'].rolling(window=window_size).mean()


# Calculate IQR for latency
Q1 = df_success['latency'].quantile(0.25)
Q3 = df_success['latency'].quantile(0.75)
IQR = Q3 - Q1

# Define bounds for outliers
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter out outliers
df_filtered = df_success[(df_success['latency'] >= lower_bound) & (df_success['latency'] <= upper_bound)]

# Calculate moving average on filtered data
window_size = 50  # Adjust based on your preference
df_filtered['latency_ma'] = df_filtered['latency'].rolling(window=window_size).mean()

# Plotting with moving average, excluding outliers
# Identify indices where status changes from 'success' to 'fail'
start_migration_changes = (df['status'].shift(1) == 'success') & (df['status'] == 'fail')

# Convert 't_relative' for the points of status change
start_change_points = df.loc[start_migration_changes, 't_relative']

# Identifying indices where status changes from 'fail' to 'success' for end of migration
end_migration_changes = (df['status'].shift(1) == 'fail') & (df['status'] == 'success')

# Convert 't_relative' for the points of end of migration
end_change_points = df.loc[end_migration_changes, 't_relative']

# Now plotting, including your existing plot code for latency
sns.set_theme()
plt.figure(figsize=(10, 6))


colors = sns.color_palette("deep", n_colors=5)
blue = colors[0]
orange = colors[1]
green = colors[2]
red = colors[3]


sns.scatterplot(data=df_filtered, x='t_relative', y='latency', alpha=0.5, s=20, color=orange, label='Raw latency')
sns.lineplot(data=df_filtered, x='t_relative', y='latency_ma', color=red, label='Moving average')

# Mark the status change points on the x-axis with vertical lines
for cp in start_change_points:
    plt.axvline(x=cp, color=blue, linestyle=':', label='Start of migration' if cp == start_change_points.iloc[0] else "")
    
# Mark the end of migration change points on the x-axis with vertical lines
for ecp in end_change_points:
    plt.axvline(x=ecp, color=green, linestyle=':', label='End of migration' if ecp == end_change_points.iloc[0] else "")


plt.xlabel("Time (s)")
plt.ylabel("Request latency (ms)")
plt.legend()
plt.savefig(f'../../fig/client_latency_scatter_{file_name_without_extension}.pdf', dpi=1000, format='pdf')
plt.close()