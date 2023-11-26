from setuptools import setup, find_packages

# with open("./requirements.txt") as f:
#     requirements = f.read().splitlines()

setup(
    name="celestial-container-migration-scripts",
    version="0.5.0",
    packages=find_packages(where="src"),
    # install_requires=requirements,
    py_modules=[
        "generate_random_data",
        "get_redis",
        "migrate_container",
        "redis_client",
        "remove_container",
        "remove_volume",
        "set_redis",
        "start_container",
        "stop_container",
    ],
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
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
