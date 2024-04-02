SHELL := /bin/bash

.PHONY: all sat gst client

all: sat gst client
sat: cleansat satserver satimg
gst: cleangst gstserver gstimg
client: cleanclient gstclient clientimg

cleansat:
	rm -rf ~/celestial-container-migration/celestial-app/sat.img ~/celestial-container-migration/celestial-app/celestial_container_migration_sat_server*.whl

cleangst:
	rm -rf ~/celestial-container-migration/celestial-app/gst.img ~/celestial-container-migration/celestial-app/celestial_container_migration_gst_server*.whl

cleanclient:
	rm -rf ~/celestial-container-migration/celestial-app/client.img ~/celestial-container-migration/celestial-app/celestial_container_migration_gst_client*.whl

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

gstclient:
	cd ~/celestial-container-migration/packages/gst_client && \
	source .venv/bin/activate && \
	pip install . && \
	python3 setup.py sdist bdist_wheel && \
	mv dist/celestial_container_migration_gst_client-0.6.0-py3-none-any.whl ~/celestial-container-migration/celestial-app
		
satimg: sat.sh sat-base.sh redis-alpine.tar.gz celestial_container_migration_sat_server-0.6.0-py3-none-any.whl containers.conf celestial.toml redis.conf
	@docker run --rm -v $(PWD)/sat.sh:/app.sh -v $(PWD)/sat-base.sh:/base.sh -v $(PWD)/celestial.toml:/files/celestial.toml -v $(PWD):/opt/code -v $(PWD)/redis-alpine.tar.gz:/files/redis-alpine.tar.gz -v $(PWD)/celestial_container_migration_sat_server-0.6.0-py3-none-any.whl:/files/celestial_container_migration_sat_server-0.6.0-py3-none-any.whl -v $(PWD)/containers.conf:/files/containers.conf -v $(PWD)/redis.conf:/files/redis.conf --privileged rootfsbuilder sat.img

gstimg: gst.sh gst-base.sh celestial_container_migration_gst_server-0.6.0-py3-none-any.whl
	@docker run --rm -v $(PWD)/gst.sh:/app.sh -v $(PWD)/gst-base.sh:/base.sh -v $(PWD):/opt/code -v $(PWD)/celestial_container_migration_gst_server-0.6.0-py3-none-any.whl:/files/celestial_container_migration_gst_server-0.6.0-py3-none-any.whl --privileged rootfsbuilder gst.img

clientimg: client.sh client-base.sh celestial_container_migration_gst_client-0.6.0-py3-none-any.whl
	@docker run --rm -v $(PWD)/client.sh:/app.sh -v $(PWD)/client-base.sh:/base.sh -v $(PWD):/opt/code -v $(PWD)/celestial_container_migration_gst_client-0.6.0-py3-none-any.whl:/files/celestial_container_migration_gst_client-0.6.0-py3-none-any.whl --privileged rootfsbuilder client.img
		