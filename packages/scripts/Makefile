SHELL := /bin/bash


.PHONY: all

all: plots

plots:
	@echo "Activating venv..." && \
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	printf "Installing required packages...\n" && \
	pip install . && \
	printf "Generating plots...\n" && \
	./generate.sh \