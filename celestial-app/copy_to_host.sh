#!/bin/bash

# Assign the first argument to INSTANCE_INDEX
INSTANCE_INDEX=$1

GCP_REGION="europe-west3"
GCP_ZONE="a"
HOST_INSTANCE="celestial-host-$INSTANCE_INDEX"

# Make sure to change the paths
CELESTIAL_PATH="/home/stanley/celestial"
CELESTIAL_CONTAINER_MIGRATION_PATH="/home/stanley/celestial-container-migration"

# Copy binary and images to the specific host instance
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    $CELESTIAL_PATH/celestial.bin $HOST_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    $CELESTIAL_CONTAINER_MIGRATION_PATH/celestial-app/sat.img $HOST_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    $CELESTIAL_CONTAINER_MIGRATION_PATH/celestial-app/gst.img $HOST_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    $CELESTIAL_CONTAINER_MIGRATION_PATH/celestial-app/client.img $HOST_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    $CELESTIAL_CONTAINER_MIGRATION_PATH/firecracker/vmlinux.bin $HOST_INSTANCE:.

# Move the files to their respective directories on the host
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo mv sat.img /celestial/sat.img"
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo mv gst.img /celestial/gst.img"
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo mv client.img /celestial/client.img"
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo mv vmlinux.bin /celestial/vmlinux.bin"

# Reboot the host
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo reboot now"

sleep 20

# Infinite loop to keep trying SSH every 5 seconds
while true; do
    sleep 5

    gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
        --command "sudo systemctl stop systemd-resolved ; sudo ./celestial.bin"
done
