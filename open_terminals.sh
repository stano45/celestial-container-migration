#!/bin/bash

# Terminal 1
gnome-terminal -- /bin/bash -c "cd /home/username/test/celestial-container-migration; source .venv/bin/activate; python3 client.py; exec bash"
sleep 1
wmctrl -r :ACTIVE: -e 0,0,0,1920,540  # Adjust 1920,540 according to your screen resolution (half of the vertical resolution)

# Terminal 2
gnome-terminal -- /bin/bash -c "cd /home/username/test/celestial-container-migration; source .venv/bin/activate; python3 server.py; exec bash"
sleep 1
wmctrl -r :ACTIVE: -e 0,0,540,1920,540  # Adjust 1920,1080 according to your screen resolution
