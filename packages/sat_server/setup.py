from setuptools import setup, find_packages

with open("./requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="celestial-container-migration-sat-server",
    version="0.6.0",
    packages=find_packages(where="src"),
    install_requires=requirements,
    py_modules=[
        "sat_server",
        "checkpoint",
        "restore",
        "utils",
        "config",
        "podman_client",
    ],
    package_dir={"": "src"},
    entry_points={
        "console_scripts": ["start-sat-server=sat_server:main"],
    },
)
