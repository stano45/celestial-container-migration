gcloud compute ssh celestial-host-0 --command "mkdir -p ./tmp && sudo mount /celestial/ceberlin.ext4 ./tmp -o loop && cp ./tmp/root/migration.csv . && sudo umount ./tmp && rmdir ./tmp"
gcloud compute scp celestial-host-0:./migration.csv ./migration.csv

gcloud compute ssh celestial-host-0 --command "mkdir -p ./tmp && sudo mount /celestial/ceclient.ext4 ./tmp -o loop && cp ./tmp/root/client.csv . && sudo umount ./tmp && rmdir ./tmp"
gcloud compute scp celestial-host-0:./client.csv ./client.csv

# cd
# mkdir -p ./tmp
# sudo mount /celestial/ceberlin.ext4 ./tmp -o loop
# cp ./tmp/root/migration.csv .
# sudo umount ./tmp
# rmdir ./tmp
# gcloud compute scp celestial-host-0:./client.csv ./client.csv

# cd
# mkdir -p ./tmp
# sudo mount /celestial/ceclient.ext4 ./tmp -o loop
# cp ./tmp/root/client.csv .
# sudo umount ./tmp
# rmdir ./tmp

# ls
# exit

# gcloud compute scp celestial-host-0:./client.csv ./client.csv
