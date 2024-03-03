import os
import random
import string
import sys
import time
from tqdm import tqdm
import redis


def generate_random_string(bytes):
    """Generate a random string of given length."""

    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(bytes)
    )


def write_data(redis_client, keys_count, bytes_per_key):
    # run_command(
    #     f"podman exec redis redis-cli "
    #     f"DEBUG POPULATE {keys_count} key {bytes_per_key}"
    # )
    start = time.time()
    pipe = redis_client.pipeline()
    # data = {}
    # for i in tqdm(
    #     range(1, keys_count + 1), desc="Writing data", ncols=100
    # ):
    for i in range(1, keys_count + 1):
        key = f"key{i}"
        # value = generate_random_string(bytes_per_key)
        # redis_client.set(key, value)
        value = os.urandom(bytes_per_key)
        pipe.set(key, value)
        if i % 1000 == 0:  # Execute every 1000 commands
            pipe.execute()
            pass
    # return data
    pipe.execute()
    end = time.time()
    print(f"Time to write {keys_count} keys: {end - start} seconds")


def verify_data(redis_client, data):
    for key, original_value in data.items():
        clone_value = redis_client.get(key)
        if original_value != clone_value:
            raise RuntimeError(
                f"Data mismatch for key {key} between saved "
                "data and cloned container!"
            )


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python write_redis.py "
            "<redis_ip> <data_size_mb> <bytes_per_key>"
        )
        sys.exit(1)

    redis_ip = sys.argv[1]
    data_size_mb = int(sys.argv[2])
    bytes_per_key = int(sys.argv[3])

    redis_client = redis.Redis(host=redis_ip, port=6379, decode_responses=True)

    if redis_client is None:
        print("Redis client is None")
        sys.exit(1)

    if redis_client.ping() is False:
        print("Redis client ping failed")
        sys.exit(1)

    keys_count = (data_size_mb * 1024 * 1024) // bytes_per_key
    print(f"Writing {keys_count} keys with {bytes_per_key} bytes per key")
    known_key_values = write_data(
        redis_client=redis_client,
        keys_count=keys_count,
        bytes_per_key=bytes_per_key,
    )

    print(f"Finished writing {keys_count} keys")

    # print("Verifying data...")
    # try:
    #     verify_data(redis_client=redis_client, data=known_key_values)
    # except Exception as err:
    #     print("Error verifying data: ", err)
    # else:
    #     print("Data verified successfully")


if __name__ == "__main__":
    main()
