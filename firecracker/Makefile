.PHONY: all

all: vm1 vm2

vm1:
	@sudo rm -f /tmp/firecracker.socket && firecracker --api-sock /tmp/firecracker.socket --config-file vm_config_network.json

vm2:
	@sudo rm -f /tmp/firecracker1.socket && firecracker --api-sock /tmp/firecracker1.socket --config-file vm1_config_network.json
