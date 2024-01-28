#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_ip> <destination_ip>"
    exit 1
fi

# Assign the arguments to variables
source_ip=$1
destination_ip=$2

# Execute the migration command
migrate-container $source_ip $destination_ip redis

# Send a notification
curl -X POST http://127.0.0.1:5000/notify \
    -H "Content-Type: application/json" \
    -d "{\"sat\": \"$destination_ip\"}"
