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

# the base script install all the necessary dependencies during root
# filesystem compilation


# Install build dependencies
printf "\nInstalling build dependencies...\n"
apk add git build-base make python3 py3-pip py3-virtualenv py3-wheel

# Proto libs for CRIU
printf "\nInstalling proto libs for CRIU...\n"
apk add protobuf protobuf-c protobuf-c-dev protobuf-dev protoc 

# CRIU deps
printf "\nInstalling CRIU dependencies...\n"
apk add pkgconfig py-ipaddress libbsd-dev iproute2 nftables libcap-dev libnet-dev libnl3-dev libaio-dev gnutls-dev py3-future libdrm-dev libbsd-dev
apk add asciidoc xmlto

# Podman
printf "\nInstalling Podman...\n"
apk add podman tar runc
podman -v || exit 1

# CRIU
printf "\nInstalling CRIU...\n"
cd
git clone https://github.com/checkpoint-restore/criu.git
cd criu
make install -j$(nproc)
cp ./criu/criu /sbin
criu --version || exit 1

printf "\nInstalling migration server...\n"
cd /celestial-container-migration
python3 -m venv .venv
source .venv/bin/activate
pip install .