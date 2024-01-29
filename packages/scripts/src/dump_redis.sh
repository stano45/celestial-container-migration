podman exec redis redis-cli SAVE
podman cp redis:/data/dump.rdb ./dump.rdb
