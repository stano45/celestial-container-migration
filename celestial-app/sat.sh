#!/bin/sh

# # let's get the gateway IP by parsing "/sbin/ip route"
# # we need this to set our nameserver here
IP=$(/sbin/ip route | awk '/default/ { print $3 }')

# # set the nameserver to our gateway IP
# # this way, we can use the helpful X.Y.celestial DNS service
echo nameserver "$IP" > /etc/resolv.conf

mkdir /var/tmp
podman load -i redis-alpine.tar.gz

criu check --all

source .server-venv/bin/activate
# printf "Starting SAT server...\n"
# start-sat-server
# start shell
/bin/sh