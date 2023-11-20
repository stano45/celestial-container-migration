apk add git build-base make py3-pip
apk add protobuf protobuf-c protobuf-c-dev protobuf-dev protoc 
apk add pkgconfig py-ipaddress libbsd-dev iproute2 nftables libcap-dev libnet-dev libnl3-dev libaio-dev gnutls-dev py3-future libdrm-dev libbsd-dev
apk add asciidoc xmlto

apk add podman tar runc
rc-update add cgroups
rc-service cgroups start