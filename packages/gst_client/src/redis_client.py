import random
import string
import redis
from tqdm import tqdm
import logging


class RedisClient:
    def __init__(self, host, port=6379, socket_timeout=1):
        self.host = host
        self.port = port
        self.socket_timeout = socket_timeout
        self.client = self._create_client()
        self.disable_persistence()

    def _create_client(self):
        return redis.Redis(
            host=self.host,
            port=self.port,
            decode_responses=True,
            socket_timeout=self.socket_timeout,
        )

    def reconnect(self, new_host):
        if new_host != self.host:
            self.host = new_host
            self.client = self._create_client()
            self.disable_persistence()
            logging.info(f"Reconnected to new host: {self.host}")

    def get_host(self):
        return self.host

    def get(self, key):
        try:
            value = self.client.get(key)
            return value
        except Exception as err:
            print(f"Error getting key {key}: {err=}, {type(err)=}")
            raise

    def set(self, key, value):
        try:
            self.client.set(key, value)
        except Exception as err:
            print(f"Error setting key {key}: {err=}, {type(err)=}")
            raise

    def delete(self, key):
        try:
            self.client.delete(key)
        except Exception as err:
            print(f"Error deleting key {key}: {err=}, {type(err)=}")
            raise

    def close(self):
        self.client.close()

    def __del__(self):
        self.client.close()

    def save(self):
        self.client.save()

    def disable_persistence(self):
        self.client.config_set("save", "")
        self.client.config_set("appendonly", "no")
        logging.info(f"Persistence disabled for redis {self.host}")

    def write_data(self, keys_count, bytes_per_key):
        data = {}
        for i in tqdm(
            range(1, keys_count + 1), desc="Writing data", ncols=100
        ):
            key = f"key{i}"
            value = self._generate_random_string(bytes_per_key)
            self.client.set(key, value)
            data[key] = value
        return data

    def verify_data(self, data):
        for key, original_value in data.items():
            clone_value = self.client.get(key)
            if original_value != clone_value:
                raise RuntimeError(
                    f"Data mismatch for key {key} between saved "
                    "data and cloned container!"
                )

    @staticmethod
    def _generate_random_string(bytes):
        """Generate a random string of given length."""

        return "".join(
            random.choice(string.ascii_letters + string.digits)
            for _ in range(bytes)
        )
