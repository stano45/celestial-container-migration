# Scripts
This directory contains python and bash scripts for:
- Generating figures for the thesis,
- Interacting with a local Redis server.

To re-generate all plots from files in `/data`, run:
```bash
make
```
This will:
1. Create a virtual environment in `.venv` and install the required packages.
2. Run `./generate.sh` which triggers all required scripts to generate the figures.

All figures will be saved in the `/fig` directory in .pdf format.