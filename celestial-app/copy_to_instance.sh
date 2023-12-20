# copy image and binary to hosts
# adapt this if you change the name or amount of hosts

GCP_REGION="europe-west3"
GCP_ZONE="a"

for i in 0 1; do
    HOST_INSTANCE="celestial-host-$i"
    gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
        ~/celestial/celestial.bin $HOST_INSTANCE:.
    gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
        ~/celestial-container-migration/firecracker/sat.img $HOST_INSTANCE:.
    gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
        ~/celestial-container-migration/firecracker/gst.img $HOST_INSTANCE:.
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
done
