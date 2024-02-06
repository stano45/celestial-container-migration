#!/bin/sh

# Check for the correct number of arguments
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <size_in_mb> <filename>"
  exit 1
fi

# Extract arguments
SIZE_IN_MB=$1
FILENAME=$2

# Step 1: Create a file of specified size in MB
dd if=/dev/zero of="$FILENAME" bs=1M count=$SIZE_IN_MB

# Step 2: Format the file with an ext4 filesystem
mkfs.ext4 "$FILENAME"

echo "Created and formatted $FILENAME with ext4 filesystem, size ${SIZE_IN_MB}MB."
