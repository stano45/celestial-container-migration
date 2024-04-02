#!/bin/bash

# Assign the first argument to INSTANCE_INDEX
INSTANCE_INDEX=0

GCP_REGION="europe-west3"
GCP_ZONE="a"
HOST_INSTANCE="celestial-host-$INSTANCE_INDEX"

# Make sure to change the path
CELESTIAL_CONTAINER_MIGRATION_PATH="/home/stanley/celestial-container-migration"

# Copy binary and images to the specific host instance
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    $CELESTIAL_CONTAINER_MIGRATION_PATH/celestial-app/gst.img $HOST_INSTANCE:.

# Move the files to their respective directories on the host
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo kill -9 `sudo lsof -t -i:1969` ; sudo mv gst.img /celestial/gst.img && sudo rm -rf /celestial/out && sudo rm -rf /celestial/*.ext4 && sudo reboot now"

sleep 20

# Infinite loop to keep trying SSH every 5 seconds
while true; do
    sleep 5

    gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
        --command "sudo systemctl stop systemd-resolved ; sudo ./celestial.bin"
done
