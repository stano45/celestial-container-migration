# Celestial Related Files and Configuration
This directory contains scripts, configuration files and other resources to deploy the migration orchestrator on Celestial and to run the experiments.

To successfully build and deploy this application, run experiments, and copy the results, you need to do the following:
1. [Build SquashFS images](#building-squashfs-images) for the servers and the client.
2. [Build a Linux kernel](#building-a-linux-kernel) for the microVMs.
3. [Deploy the system](#deploying-the-system) on Celestial and run experiments.
4. [Copy results](#copying-results) from the VMs to your machine.

Make sure to run `terraform destroy` after you're done with the experiments to avoid unnecessary charges.

## Building SquashFS Images
### Prerequisites
- `make`
- `docker`
- `pip`
- `python3`
- `rootfsbuilder` tool from the Celestial repo.


### Building Images

To build all images (`gst.img`, `sat.img`, `client.img`), run the following command:
```bash
make
```

This command will:
1. Remove any existing images in the `celestial-app` directory (`gst.img`, `sat.img`, `client.img`).
2. Build wheels for all three servers in `packages/sat_server`, `packages/gst_server` and `packages/gst_client`.
3. Move the wheels to the `celestial-app` directory.
4. Build the images using `rootfsbuilder`.

## Building a Linux Kernel
The firecracker microVMs require a custom Linux kernel to enable required kernel flags for CRIU. We provided a config file [`/celestial-app/.vmlinux-5.15.138`](/celestial-app/.vmlinux-5.15.138.config) which can be used to build the kernel (for Linux 5.15.138). To build the kernel, follow the instructions provided by Celestial [here](https://openfogstack.github.io/celestial/kernel). Once you're done building the kernel, place it into `celestial-app` directory. This is crucial for the deployment scripts to work.

## Deploying & Running Experiments
1. Deploy Celestial's infrastructure. Celestial has recently become cloud-agnostic, but this project still runs on GCP. To deploy Celestial on GCP, follow the instructions within the Celestial repo. Make sure to use our custom `main.tf` and `variables.tf` files in the `terraform` directory in this repo. For more info, see the README in the `terraform` directory.

2. Once both VMs are up and running, use the following scripts:
   - `./copy_to_host.sh 0` to copy all required resources to host 0 (the only one) move them to the correct directories, restart the instance, wait for it to boot, and then start a Celestial instance.

   - `./copy_to_coord.sh` to copy all required resources to the coordinator instance, build the Celestial Docker image and ssh into the coordinator.

   - Once both the host and coordinator are ready, run `sudo docker run --rm -it -p 8000:8000 -v $(pwd)/celestial.toml:/config.toml celestial /config.toml` in the coordinator shell to start the experiments.

## Copying Results
To copy results from the VMs to your machine, use the following script:
```
./copy_results.sh
```
This will copy the `migration.csv` and `client.csv` files from the VMs to the `celestial-app` directory.