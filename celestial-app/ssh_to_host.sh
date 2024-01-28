# Assign the first argument to INSTANCE_INDEX
INSTANCE_INDEX=$1
HOST_INSTANCE="celestial-host-$INSTANCE_INDEX"
gcloud compute ssh --zone="europe-west3-a" $HOST_INSTANCE