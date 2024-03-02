#!/bin/bash

# Get 2 args
# 1. migration file name
# 2. client file name
# 3. plot title

if [ "$#" -ne 3 ]; then
    echo "Usage: generate_plots_for_experiment.sh [migration_file_name] [client_file_name] [plot_title]"
    exit 1
fi

migration_file_name=$1
client_file_name=$2
plot_title=$3

SCRIPT_PATH=$(dirname $(realpath -s $0))
PYTHON_FILES=$SCRIPT_PATH/src

echo "Migration file name: $migration_file_name"
echo "Client file name: $client_file_name"

echo "Generating availability plot..."
python3 $PYTHON_FILES/plot_availability_over_time.py $client_file_name "$plot_title"

echo "Generating migration stats..."
python3 $PYTHON_FILES/stats_downtime.py "$client_file_name" "$migration_file_name"

echo "Generating criu plot..."
python3 $PYTHON_FILES/plot_criu_speed_pie_chart.py $migration_file_name "$plot_title"

# echo "Generating migration line plot..."
# python3 $PYTHON_FILES/plot_migration_speed_line_chart.py $migration_file_name "$plot_title"
