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
SHELL := /bin/bash

.PHONY: all sat gst

all: satserver gstserver satimg gstimg
sat: satserver satimg
gst: gstserver gstimg

satserver:
	cd ~/celestial-container-migration/packages/sat_server && \
	source .venv/bin/activate && \
	pip install . && \
	python3 setup.py sdist bdist_wheel && \
	mv dist/celestial_container_migration_sat_server-0.6.0-py3-none-any.whl ~/celestial-container-migration/celestial-app

gstserver:
	cd ~/celestial-container-migration/packages/gst_server && \
	source .venv/bin/activate && \
	pip install . && \
	python3 setup.py sdist bdist_wheel && \
	mv dist/celestial_container_migration_gst_server-0.6.0-py3-none-any.whl ~/celestial-container-migration/celestial-app
	
satimg: sat.sh sat-base.sh redis-alpine.tar.gz celestial_container_migration_sat_server-0.6.0-py3-none-any.whl containers.conf celestial.toml
	@docker run --rm -v $(PWD)/sat.sh:/app.sh -v $(PWD)/sat-base.sh:/base.sh -v $(PWD)/celestial.toml:/files/celestial.toml -v $(PWD):/opt/code -v $(PWD)/redis-alpine.tar.gz:/files/redis-alpine.tar.gz -v $(PWD)/celestial_container_migration_sat_server-0.6.0-py3-none-any.whl:/files/celestial_container_migration_sat_server-0.6.0-py3-none-any.whl -v $(PWD)/containers.conf:/files/containers.conf --privileged rootfsbuilder sat.img

gstimg: gst.sh gst-base.sh celestial_container_migration_gst_server-0.6.0-py3-none-any.whl
	@docker run --rm -v $(PWD)/gst.sh:/app.sh -v $(PWD)/gst-base.sh:/base.sh -v $(PWD):/opt/code -v $(PWD)/celestial_container_migration_gst_server-0.6.0-py3-none-any.whl:/files/celestial_container_migration_gst_server-0.6.0-py3-none-any.whl --privileged rootfsbuilder gst.img
	