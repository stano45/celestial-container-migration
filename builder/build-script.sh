#!/bin/bash

#
# This file is part of Celestial (https://github.com/OpenFogStack/celestial).
# Copyright (c) 2021 Tobias Pfandzelter, The OpenFogStack Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# $1 = filename for your rootfs

mkdir -p ./tmp || exit 1

cp -r  minirootfs/* ./tmp/ || exit 1

# if you don't do this, apk can't access its repositories
cp /etc/resolv.conf ./tmp/etc/resolv.conf || exit 1
cp interfaces ./tmp/etc/network/interfaces || exit 1
cp inittab ./tmp/etc/inittab || exit 1
cp start-script ./tmp/start.sh || exit 1
cp /app.sh ./tmp/app.sh || exit 1
mkdir -p ./tmp/dev/
mount --bind /dev ./tmp/dev/

if [ -d "/files" ]; then
    cp -rv /files/* ./tmp/ || exit 1
fi

cat > ./tmp/prepare.sh <<EOF
passwd root -d root
apk add -u openrc ca-certificates
rc-update add devfs boot
rc-update add procfs boot
rc-update add sysfs boot
exit
EOF

if [ -d "/files" ]; then
    cp -rv /files/* ./tmp/
fi

chroot ./tmp/ /bin/sh /prepare.sh || exit 1

if [ -f "/base.sh" ]; then
    cp /base.sh ./tmp/base.sh
    chroot ./tmp/ /bin/sh base.sh
    rm ./tmp/base.sh
fi

# these are the mount points we need to create
mkdir -p ./tmp/overlay/root \
    ./tmp/overlay/work \
    ./tmp/mnt \
    ./tmp/rom \
    || exit 1

# now switch back to a public name server
echo nameserver 1.1.1.1 > ./tmp/etc/resolv.conf

rm ./tmp/prepare.sh

mksquashfs ./tmp rootfs.img -noappend || exit 1

mv rootfs.img /opt/code/"$1"