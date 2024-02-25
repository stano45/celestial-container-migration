import logging
import random
import sys
import threading
import time
from flask import Flask, request, has_request_context
from redis_client import RedisClient

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    stream=sys.stdout,
)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.method = request.method
        else:
            record.url = None
            record.method = None
        # Custom formatting to exclude 'None' values
        if record.url is None and record.method is None:
            log_format = (
                "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            )
        else:
            log_format = (
                "[%(asctime)s] %(levelname)s in %(module)s "
                "[%(url)s] [%(method)s]: %(message)s"
            )

        formatter = logging.Formatter(log_format)
        return formatter.format(record)


# Custom Formatter
formatter = RequestFormatter(
    "[%(asctime)s] %(levelname)s in %(module)s "
    "[%(url)s] [%(method)s]: %(message)s"
)

for handler in logging.getLogger().handlers:
    handler.setFormatter(formatter)

app = Flask(__name__)


# Global state
redis_client: RedisClient = None
known_key_values = {}


@app.route("/notify", methods=["POST"])
def notify():
    data = request.json
    if "host" in data:
        current_sat = data["host"]
        global redis_client
        try:
            if redis_client is None:
                redis_client = RedisClient(
                    host=current_sat, socket_timeout=0.1
                )
            else:
                redis_client.reconnect(new_host=current_sat)
        except Exception as err:
            logging.error(err)
        return {"message": f"Switched Redis host: {current_sat}"}, 200
    return {"error": "host not provided"}, 400


def build_entry(start, host, op, status, error, latency):
    return f"{start},{host},{op},{status},{error},{latency}\n"


def run_operation(op):
    global known_key_values
    global redis_client
    logging.info(f"Performing {op} operation")
    if op == "set":
        key = random.randint(0, 100000)
        value = random.randint(0, 100000)
        redis_client.set(key, value)
        known_key_values[key] = f"{value}"
        return
    elif op == "get":
        if len(known_key_values) == 0:
            key = random.randint(0, 100000)
        else:
            key = random.choice(list(known_key_values.keys()))
        # expected_value = known_key_values.get(key)
        # actual_value = redis_client.get(key)
        redis_client.get(key)
        # if expected_value != actual_value:
        #     error = f"Value mismatch: {expected_value=} - {actual_value=}"
        #     logging.error(error)
        #     raise ValueError(error)
        return
    elif op == "del":
        if len(known_key_values) == 0:
            key = random.randint(0, 100000)
        else:
            key = random.choice(list(known_key_values.keys()))
        redis_client.delete(key)
        known_key_values.pop(key, None)


def test_redis(requests_per_second=10):
    global redis_client
    global known_key_values

    logging.info(f"Starting redis client daemon with {requests_per_second=}")

    while redis_client is None:
        logging.info("Waiting for host notification...")
        time.sleep(1)

    operations = ["set", "get", "del"]
    request_interval = 1 / requests_per_second
    with open("client.csv", "w", newline="\n", encoding="utf-8") as f:
        f.write("t," "host," "operation," "status," "error," "latency\n")
        while True:
            time.sleep(request_interval)
            logging.info(f"Using redis host {redis_client.get_host()}")

            op = random.choice(operations)
            start = time.time()

            try:
                run_operation(op)
            except Exception as err:
                logging.error(err)
                entry = build_entry(
                    start=start,
                    host=redis_client.get_host(),
                    op=op,
                    status="fail",
                    error=err,
                    latency=time.time() - start,
                )
                logging.info(f"Writing entry to file {entry=}")
                f.write(entry)
            else:
                entry = build_entry(
                    start=start,
                    host=redis_client.get_host(),
                    op=op,
                    status="success",
                    error="",
                    latency=time.time() - start,
                )
                logging.info(f"Writing entry to file {entry=}")
                f.write(entry)
            f.flush()


def main():
    if len(sys.argv) != 2:
        exit(
            "Usage: python3 gst_client.py [gateway]\n   "
            "OR: start-gst-client [gateway]"
        )
    gateway = sys.argv[1]
    logging.info(f"Hello from redis client! Gateway is {gateway}")

    # Start sending requests to redis
    threading.Thread(target=test_redis).start()

    # Expose notify endpoint
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
