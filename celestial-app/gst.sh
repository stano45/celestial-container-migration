# # we need this to set our nameserver here
IP=$(/sbin/ip route | awk '/default/ { print $3 }')
REDIS_INSTANCE_SIZE_MB=5000
CHECK_PERIOD=5
BYTES_PER_KEY=128000

# # set the nameserver to our gateway IP
# # this way, we can use the helpful X.Y.celestial DNS service
echo nameserver "$IP" > /etc/resolv.conf

printf "Starting GST server...\n"
source .server-venv/bin/activate

# Usage: start-gst-server [gateway] [check_period] [instance_size_mb] [bytes_per_key]"
start-gst-server $IP $CHECK_PERIOD $REDIS_INSTANCE_SIZE_MB $BYTES_PER_KEY
