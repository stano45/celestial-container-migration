# Terraform Configuration for Celestial
This directory contains the Terraform configuration files for the deployment of Celestial.  Simply copy these files to Celestial's terraform directory and run `terraform plan` to see what will be deployed and `terraform apply` to deploy the instances.

Note: Make sure to add your project ID to the `variables.tf` file.

## What is Deployed
The Terraform configuration deploys the following resources:
1. One `n2-custom-8-307200-ext` host instance with 8 vCPUs, 307200 MB of memory and 500 GB of `pd-ssd` storage.
2. One `e2-standard-8` instance with 8 vCPUs, 8 GB of memory and 10 GB of storage.
3. Whatever else Celestial configures (networking, etc.).

See the [Compute Engine Documentation](https://cloud.google.com/compute/docs/machine-types) for more information on the instance types.

## Warning
The configured host type is `n2-custom-8-307200-ext`, which is a custom `n2` instance with 307200 MB of memory.  Proceed with caution as provisioning this instance is expensive. Make sure to run `terraform destroy` after you are done with the experiments.