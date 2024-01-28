# # we need this to set our nameserver here
IP=$(/sbin/ip route | awk '/default/ { print $3 }')

# # set the nameserver to our gateway IP
# # this way, we can use the helpful X.Y.celestial DNS service
echo nameserver "$IP" > /etc/resolv.conf

printf "Starting GST client...\n"
source .client-venv/bin/activate
start-gst-client $IP