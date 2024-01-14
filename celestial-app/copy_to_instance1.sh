# copy image and binary to hosts
# adapt this if you change the name or amount of hosts

GCP_REGION="europe-west3"
GCP_ZONE="a"
HOST_INSTANCE="celestial-host-1"
CELESTIAL_PATH="/home/stanley/celestial"


gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    $CELESTIAL_PATH/celestial.bin $HOST_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    ~/celestial-container-migration/celestial-app/sat.img $HOST_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    ~/celestial-container-migration/celestial-app/gst.img $HOST_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    ~/celestial-container-migration/firecracker/vmlinux.bin $HOST_INSTANCE:.

gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo mv sat.img /celestial/sat.img"
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo mv gst.img /celestial/gst.img"
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo mv vmlinux.bin /celestial/vmlinux.bin"

# before we start, we need to reboot our hosts once
# the reason is that we need to adapt file descriptor limits, which we do
# with terraform during setup but which requires a reboot after
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo reboot now"

sleep 10

# Infinite loop to keep trying SSH every 5 seconds
while true; do
    sleep 5

    gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $HOST_INSTANCE \
    --command "sudo systemctl stop systemd-resolved ; sudo ./celestial.bin"
done
