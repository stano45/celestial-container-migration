import sys
import pandas as pd
import matplotlib.pyplot as plt


def main():
    if len(sys.argv) != 2:
        print("Usage: plot-migration-data <csv_file>")
        sys.exit(1)
    file_path = sys.argv[1]

    # Read the CSV file
    df = pd.read_csv(file_path)

    # Convert the 't' column to datetime
    df["t"] = pd.to_datetime(df["t"], unit="s")

    # Format the 't' column to show time in hh:mm:ss
    df["t"] = df["t"].dt.strftime("%H:%M:%S")

    # Convert durations from milliseconds to seconds
    duration_columns = [
        "total_duration",
        "checkpoint_duration",
        "restore_duration",
    ]
    df[duration_columns] = df[duration_columns] / 1000  # Convert ms to s

    # Plotting
    plt.figure(figsize=(15, 10))

    # Plot each column (except 't', 'source_sat', 'target_sat')
    for column in df.columns[3:]:
        plt.plot(df["t"], df[column], label=column, marker="o")

        # Annotate durations and source-target pairs
        for i, (t, duration) in enumerate(zip(df["t"], df[column])):
            annotation_text = f"{duration:.2f}s\n({df.loc[i, 'source_sat']},{df.loc[i, 'target_sat']})"
            plt.annotate(
                annotation_text,
                (t, duration),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=8,
            )

    plt.xlabel("Timestamp")
    plt.ylabel("Duration (s)")
    plt.title("Live Container Migration Duration")
    plt.legend()
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout for better fit of annotations
    plt.show()


if __name__ == "__main__":
    main()
