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

.PHONY: all

all: migration.img

migration.img: migration.sh migration-base.sh redis-alpine.tar.gz celestial_container_migration-0.4.0-py3-none-any.whl containers.conf
	@docker run --rm -v $(PWD)/migration.sh:/app.sh -v $(PWD)/migration-base.sh:/base.sh -v $(PWD):/opt/code -v $(PWD)/redis-alpine.tar.gz:/files/redis-alpine.tar.gz -v $(PWD)/celestial_container_migration-0.4.0-py3-none-any.whl:/files/celestial_container_migration-0.4.0-py3-none-any.whl -v $(PWD)/containers.conf:/files/containers.conf --privileged rootfsbuilder migration.img

	