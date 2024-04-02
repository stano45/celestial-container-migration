# Celestial Container Migration

This is the implementation part of my thesis "Evaluating the Feasibility of Proactive Container Migration on the LEO Edge". This repository contains scripts, configuration files and other resources to deploy the migration orchestrator with Celestial and to run and evaluate experiments. 

- For building, deploying the experiments, check out the [README](celestial-app/README.md) in [`celestial-app`](celestial-app).
- For examining the source code of the migration orchestrator, check out the [packages](packages) directory.
- Custom Terraform files for deploying Celestial on GCP are in the [terraform](terraform) directory.
- Figures from the thesis are in the [figures](figures) directory.
- All the collected data is in the [data](data) directory.
- For experimenting with Firecracker locally, check out the [firecracker](firecracker) directory.