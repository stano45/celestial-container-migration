# Delete the bridge and tap devices if they already exist
sudo ip link set dev br0 down
sudo brctl delbr br0
sudo ip link set dev tap0 down
sudo ip tuntap del tap0 mode tap
sudo ip link set dev tap1 down
sudo ip tuntap del tap1 mode tap

# Create the bridge and assign an IP address to the bridge
sudo brctl addbr br0
sudo ip addr add 172.16.0.10/24 dev br0
sudo ip link set dev br0 up

# Enable IP-forwarding
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
sudo iptables -t nat -A POSTROUTING -o wlp7s0 -j MASQUERADE
sudo iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Create tap0, assign it to br0 and bring it up
sudo ip tuntap add tap0 mode tap
sudo brctl addif br0 tap0
sudo ip link set tap0 up

# Create tap1, assign it to br0 and bring it up
sudo ip tuntap add tap1 mode tap
sudo brctl addif br0 tap1
sudo ip link set tap1 up

# Setup iptables to allow forwarding from tap0, tap1 to the internet
sudo iptables -A FORWARD -i tap0 -o wlp7s0 -j ACCEPT
sudo iptables -A FORWARD -i tap1 -o wlp7s0 -j ACCEPT

ip a