ip addr add 172.16.0.1/24 dev eth0
ip link set eth0 up
# Connect to bridge br0 on host
ip route add default via 172.16.0.10 dev eth0
# Google DNS server
echo "nameserver 8.8.8.8" | tee -a /etc/resolv.conf