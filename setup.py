from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="celestial-container-migration",
    version="0.4.0",
    packages=find_packages(where="src"),
    py_modules=["main_server", "migrate_container"],
    install_requires=requirements,
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "start-server=main_server:main",
            "migrate-container=scripts.migrate_container:main",
            "start-container=scripts.start_container:main",
            "stop-container=scripts.stop_container:main",
            "remove-container=scripts.remove_container:main",
            "remove-volume=scripts.remove_volume:main",
            "set-redis=scripts.set_redis:main",
            "get-redis=scripts.get_redis:main",
        ],
    },
)
