"""Check for and read new base64-encoded content from the event hub."""

import os
import sys
import time

from redis import Redis

# connect to redis
# adding auto-decoding to ease processing (python dictionary)
engine: Redis = Redis(
    password=os.environ["REDIS_PASSWORD"],
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    db=int(os.environ["REDIS_DB"]),
    charset="utf-8",
    decode_responses=True,
)

while True:
    events = engine.xread({"snapshots": "0-0"}, None, 0)
    for (id_, payload) in events[0][1]:

        # extend the code here
        print(
            f'{payload["sensor"]} @ {payload["stamp"]} :',
            f'{payload["capture"][:18]}...{payload["capture"][-18:]}'.encode()
        )

        engine.xdel("snapshots", id_)
    time.sleep(1)
