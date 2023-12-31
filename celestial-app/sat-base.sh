#!/bin/sh

#
# This file is part of Celestial (https://github.com/OpenFogStack/celestial).
# Copyright (c) 2021 Tobias Pfandzelter, The OpenFogStack Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# The base script installs all the necessary dependencies during root
# filesystem compilation


printf "\n---\nRunning base script.\n---\n"

rc-update add cgroups boot

apk add criu

# Install build dependencies
printf "\nInstalling build dependencies...\n"
apk add git musl libstdc++ alpine-sdk build-base gcompat make python3 py3-pip py3-virtualenv py3-wheel

# Proto libs for CRIU
printf "\nInstalling proto libs for CRIU...\n"
apk add protobuf protobuf-c protobuf-c-dev protobuf-dev protoc 

# CRIU deps
printf "\nInstalling CRIU dependencies...\n"
apk add pkgconfig py-ipaddress libbsd-dev iproute2 nftables nftables-dev libcap-dev libnet libnet-dev libnl3 libnl3-dev libaio-dev gnutls-dev py3-future libdrm-dev libbsd-dev libc-dev
apk add asciidoc xmlto

# CRIU
printf "\nInstalling CRIU...\n"
git clone https://github.com/checkpoint-restore/criu.git
cd criu
make install -j$(nproc)
cp ./criu/criu /sbin
criu --version || exit 1
cd ..
rm -rf criu

# Podman
printf "\nInstalling Podman...\n"
# apk add podman tar runc fuse-overlayfs
apk add podman tar runc
mv containers.conf /etc/containers/containers.conf
# mv storage.conf /etc/containers/storage.conf

podman -v

printf "\nInstalling satellite server...\n"
python3 -m venv .server-venv
source .server-venv/bin/activate
pip install /celestial_container_migration_sat_server-0.5.0-py3-none-any.whl
rm /celestial_container_migration_sat_server-0.5.0-py3-none-any.whl

# echo "nameserver 8.8.8.8" | tee -a /etc/resolv.conf

printf "\n---\nBase script finished!\n---\n"