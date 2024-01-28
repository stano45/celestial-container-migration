# gcloud compute ssh --zone="europe-west3-a" "celestial-host-0" \
# --command "sudo systemctl stop systemd-resolved ; sudo ./celestial.bin"
sudo kill -9 `sudo lsof -t -i:1969`
sudo systemctl stop systemd-resolved ; sudo ./celestial.bin