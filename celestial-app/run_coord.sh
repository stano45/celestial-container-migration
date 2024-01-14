# gcloud compute ssh --zone="europe-west3-a" celestial-coordinator \
# --command "sudo docker run --rm -it -p 8000:8000 -v $(pwd)/celestial.toml:/config.toml celestial /config.toml"
sudo docker run --rm -it -p 8000:8000 -v $(pwd)/celestial.toml:/config.toml celestial /config.toml