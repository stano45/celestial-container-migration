## Installation
1. Install `docker` and enable experimental features https://docs.docker.com/engine/install/ubuntu/ https://docs.docker.com/config/daemon/#configure-the-docker-daemon
2. Install `CRIU` (https://criu.org/Installation)

## Usage
1. Run  ```python3 main.py ```
2. If the program finished successfully, you should see a new container in the output of the docker ps command. This container is completely cloned by the original one, and the data was verified by cr.py. You can verify manually by using redis-cli.
3. If running the script again, make sure to remove the containers created by the previous run and remove the temporary checkpoints. You can do it by running the provided script: ``` ./clean.sh ```