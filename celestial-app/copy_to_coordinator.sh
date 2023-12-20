cd ~/celestial
COORDINATOR_INSTANCE="celestial-coordinator"
GCP_REGION="europe-west3"
GCP_ZONE="a"

# the first copy command can take a while because gcloud copies access keys
# to the instance
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" ~/celestial/Dockerfile $COORDINATOR_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" ~/celestial/*.py $COORDINATOR_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" ~/celestial/requirements.txt $COORDINATOR_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" --recurse \
    ~/celestial/celestial $COORDINATOR_INSTANCE:.
gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" --recurse ~/celestial/proto $COORDINATOR_INSTANCE:.

gcloud compute scp --zone="$GCP_REGION-$GCP_ZONE" \
    ~/celestial-container-migration/celestial-app/celestial.toml $COORDINATOR_INSTANCE:.

# build the coordinator
# this can take a minute, you can continue with something else
gcloud compute ssh --zone="$GCP_REGION-$GCP_ZONE" $COORDINATOR_INSTANCE \
    --command "sudo docker build -t celestial ."
