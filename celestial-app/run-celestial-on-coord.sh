sudo docker run --rm -it \
    -p 8000:8000 \
    -v $(pwd)/celestial.toml:/config.toml \
    celestial /config.toml