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

# # let's get the gateway IP by parsing "/sbin/ip route"
# # we need this to set our nameserver here
IP=$(/sbin/ip route | awk '/default/ { print $3 }')

# # set the nameserver to our gateway IP
# # this way, we can use the helpful X.Y.celestial DNS service
echo nameserver "$IP" > /etc/resolv.conf

# ip addr add 172.16.0.2/24 dev eth0
# ip link set eth0 up
# ip route add default via 172.16.0.1 dev eth0
# # Add the google DNS server
# echo "nameserver 8.8.8.8" | tee -a /etc/resolv.conf

mount -t tmpfs -o size=512M tmpfs /var
mount -t tmpfs -o size=512M tmpfs /tmp
mkdir /var/tmp

#Pull the redis alpine image
podman load -i redis-alpine.tar.gz

source .server-venv/bin/activate
# start-server

exec /bin/sh