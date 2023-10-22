import random
import string
import redis
from tqdm import tqdm


class RedisClient:
    def __init__(self, host, port=6379):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)

    def close(self):
        self.client.close()

    def __del__(self):
        self.client.close()

    def save(self):
        self.client.save()

    def disable_persistence(self):
        self.client.config_set("save", "")
        self.client.config_set("appendonly", "no")

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
