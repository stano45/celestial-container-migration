from setuptools import setup, find_packages

with open("./requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="celestial-container-migration-gst-server",
    version="0.6.0",
    packages=find_packages(where="src"),
    install_requires=requirements,
    py_modules=[
        "gst_server",
    ],
    package_dir={"": "src"},
    entry_points={
        "console_scripts": ["start-gst-server=gst_server:main"],
    },
)
