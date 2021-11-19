"""Read and push base64-encoded content every so and so."""

import os
import random
import sys
import time
import typing

from redis import Redis

# the next three objects are *just* for the randomness (and the little story)
images: typing.List[str] = next(os.walk("images"))[2]

sensor: str = os.environ["HOSTNAME"]

speeds: typing.Tuple[int] = (
    int(os.environ["LOWER_SPEED"]),
    int(os.environ["UPPER_SPEED"]),
)

# connect to redis
engine: Redis = Redis(
    password=os.environ["REDIS_PASSWORD"],
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    db=int(os.environ["REDIS_DB"]),
)

while True:
    time.sleep(random.randint(*speeds))
    payload = {
        "stamp": f"{time.time():.0f}".encode(),
        "sensor": sensor.encode(),
        "capture": open(f"images/{random.choice(images)}", "rb").read().strip(),
        "encoding": "base64(image/jpeg)",
    }
    engine.xadd("snapshots", payload)
