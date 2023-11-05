from setuptools import setup, find_packages

setup(
    name="celestial-container-migration",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "start-server=main_server:main",
        ],
    },
)
