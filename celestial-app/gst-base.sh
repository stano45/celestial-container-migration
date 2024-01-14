printf "\n---\nRunning gst img base script.\n---\n"

printf "\nInstalling build dependencies...\n"
apk add python3 py3-pip py3-virtualenv py3-wheel


printf "\nInstalling ground station server...\n"
python3 -m venv .server-venv
source .server-venv/bin/activate
pip install /celestial_container_migration_gst_server-0.6.0-py3-none-any.whl
rm /celestial_container_migration_gst_server-0.6.0-py3-none-any.whl
