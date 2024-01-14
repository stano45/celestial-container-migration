gcloud compute ssh --zone="europe-west3-a" "celestial-host-1" \
--command "sudo systemctl stop systemd-resolved ; sudo ./celestial.bin"