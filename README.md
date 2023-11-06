# Celestial Container Migration

## About 

This project is a proof-of-concept for migrating [podman](https://podman.io) containers between hosts using the [CRIU](https://criu.org) for checkpoint/restore. It consists of a server, which runs on both the source and destination hosts, and a script `migrate_container.py` to start the migration from the coordinator using the command line.

The server exposes two endpoints, `/start_migration` and `/container/<container_id>`. The `/start_migration` endpoint initiates the migration process. This is sent to the target machine (the one to which the container should be migrated). The target machine then requests the container from the source machine using the `/container` endpoint. The server also exposes a `/health` endpoint, which can be used to check if the server is running.

## Getting Started

This guide will walk you through setting up a virtual environment, installing the package, and running the `start-server` and `migrate-container` scripts.

### Prerequisites

Before you begin, ensure you have the following dependencies:
- [`podman 3.4.2+`](https://podman.io/docs/installation#ubuntu)
- [`CRIU 3.18+`](https://criu.org/Installation)
- `Python 3.x`
- `pip` (Python package manager)

*Please note that this project has only been tested on Ubuntu 20 and 22.*


### Setting Up a Virtual Environment

A virtual environment is a self-contained directory that contains a Python installation for a particular version of Python, plus a number of additional packages. To create a virtual environment, navigate to your project's root directory and run:

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

### Running the Application

After the package is installed, you can start the server with the following command:

```bash
start-server
```

This should start the server, and you will see output indicating that the server is running.


When the server is running on both the source and target VM, you can initiate container migration with the following command:

```bash
migrate-container <source-ip> <target-ip> <container-id>
```

Container ID can also be the name of the container.

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
sudo apt-get update -qq
sudo apt-get -qq -y install podman