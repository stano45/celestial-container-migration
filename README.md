# Celestial Container Migration

## About 

This project is a proof-of-concept for migrating [podman](https://podman.io) containers between hosts using the [CRIU](https://criu.org) for checkpoint/restore.

There are two servers, `sat-server` and `gst-server`, which run on satellites and ground stations respectively. The satellite server is responsible for managing containers and their migration on a single satellite. 
The ground station server is responsible for orchestrating the container migration, based on satellite positions relative to the ground station. 

The satellite server exposes two endpoints, `/start_migration` and `/container/<container_id>`. The `/start_migration` endpoint initiates the migration process. This is sent to the target machine (the one to which the container should be migrated). The target machine then requests the container from the source machine using the `/container` endpoint. The server also exposes a `/health` endpoint, which can be used to check if the server is running.

## Getting Started

There are three packages located in the `/packages` folder: `gst_server`, `sat_server` and `scripts`. These packages are all separate to ensure minimal package size. To build a package, first navigate to the package directory, for example `cd packages/gst_server`. Then follow the instructions below.


### Prerequisites

Before you begin, ensure you have the following dependencies:
- [`podman 3.4.2+`](https://podman.io/docs/installation#ubuntu)
- [`CRIU 3.18+`](https://criu.org/Installation)
- `Python 3.x`
- `pip` (Python package manager)

### Setting Up a Virtual Environment
 
To create a virtual environment, run:

```bash
python3 -m venv .venv
```

This command will create a virtual environment named `.venv` within your current directory.

### Activating the Virtual Environment

To begin using the virtual environment, it needs to be activated:

- On macOS and Linux:
  ```bash
  source .venv/bin/activate
  ```

### Installing the Package

With the virtual environment activated, install the package by running:

```bash
pip install .
```

This will install the package and its dependencies into the virtual environment.

Alternatively, you can build a wheel (useful when building a rootfs using the celestial `rootfsbuilder` image):
  
  ```bash
  pip install wheel
  python setup.py bdist_wheel
  ```



### Running the Application

After the package is installed, there are different commands to run the application depending on the package:

- **gst-server**:
  - `start-gst-server`

- **sat-server**:
  - `start-sat-server`

- **scripts**:
  - `migrate_container <source-ip> <target-ip> <container-id>`
  - `start_container <ip> <container-id>`
  - `stop_container <ip> <container-id>`
  - `remove_container <ip> <container-id>`
  - `remove_volume <ip> <volume-id>`
  - `get_redis <ip> <key>`
  - `set_redis <ip> <key> <value>`

## Troubleshooting
### Issues with installing podman on Ubuntu 20+ using the official instructions
Run:
```bash
sudo apt-get update
sudo apt-get install -y software-properties-common

ubuntu_version=$(lsb_release -rs)

sudo sh -c "echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/xUbuntu_${ubuntu_version}/ /' > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list"

wget -nv "https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/xUbuntu_${ubuntu_version}/Release.key" -O Release.key


sudo apt-key add - < Release.key
sudo apt-get update
sudo apt-get -y install podman
