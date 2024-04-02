sudo kill -9 `sudo lsof -t -i:1969`
sudo systemctl stop systemd-resolved ; sudo ./celestial.bin