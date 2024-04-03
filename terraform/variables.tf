variable "gcp_project" {
  #TODO: change this to your GCP project ID
  default = ""
}

variable "gcp_region" {
  default = "europe-west3"
}

variable "gcp_zone" {
  default = "a"
}

variable "coordinator_type" {
  default = "e2-standard-8"
}

variable "host_type" {
  default = "n2-custom-8-307200-ext"
  # default = "n2-standard-8"
}

variable "host_count" {
  default = 1
}

# change this only if you know what you're doing!
variable "image_family" {
  default = "ubuntu-2204-lts"
}

variable "image_project" {
  default = "ubuntu-os-cloud"
}
