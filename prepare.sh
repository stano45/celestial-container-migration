#!/bin/bash

sudo chown -R $(whoami) /var/lib/docker/containers/
sudo chmod -R u+w /var/lib/docker/containers/