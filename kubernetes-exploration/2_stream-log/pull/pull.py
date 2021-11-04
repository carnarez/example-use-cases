import hashlib
import logging
import os
import redis
import time

if os.environ['HOARD'].lower() in ['1', 'on', 'true', 'yes']:
    import pile

logging.basicConfig(datefmt='%Y/%m/%d %X', format='%(asctime)s: %(message)s', level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

broker = redis.Redis(
    password=os.environ.get('REDIS_PASSWORD', ''),
    host=os.environ['REDIS_HOST'],
    port=int(os.environ['REDIS_PORT'])
)

pubsub = broker.pubsub()
pubsub.subscribe('lipsum')

while True:
    message = pubsub.get_message()
    if message is not None:
        if message['type'] == 'message':
            content = message['data'].decode()
            if os.environ['HOARD'].lower() in ['1', 'on', 'true', 'yes']:
                pile.create_tables_if_not_existing()
                seconds = int(round(time.time(), 0))
                pile.insert(pile.Data(
                    id_=hashlib.sha256(f'{seconds}-{content}'.encode()).hexdigest(),
                    timestamp=seconds,
                    message=content
                ))
            logger.debug(content)
    time.sleep(int(os.environ.get('INTERVAL', 10)))
