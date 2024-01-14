from setuptools import setup, find_packages

with open("./requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="celestial-container-migration-scripts",
    version="0.5.0",
    packages=find_packages(where="src"),
    install_requires=requirements,
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
        "plot_migration_data",
    ],
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "migrate-container=migrate_container:main",
            "start-container=start_container:main",
            "stop-container=stop_container:main",
            "remove-container=remove_container:main",
            "remove-volume=remove_volume:main",
            "set-redis=set_redis:main",
            "get-redis=get_redis:main",
            "plot-migration-data=plot_migration_data:main",
        ],
    },
)
