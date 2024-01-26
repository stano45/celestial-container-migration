from setuptools import setup, find_packages

with open("./requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="celestial-container-migration-gst-client",
    version="0.6.0",
    packages=find_packages(where="src"),
    install_requires=requirements,
    py_modules=[
        "gst_client",
    ],
    package_dir={"": "src"},
    entry_points={
        "console_scripts": ["start-gst-client=gst_client:main"],
    },
)
