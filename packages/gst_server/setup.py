from setuptools import setup, find_packages

with open("./requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="celestial-container-migration-gst-server",
    version="0.5.0",
    packages=find_packages(where="src"),
    install_requires=requirements,
    py_modules=[
        "server",
    ],
    package_dir={"": "src"},
    entry_points={
        "console_scripts": ["start-gst-server=server:main"],
    },
)
