from time import sleep
from dramatiq import actor, set_broker
import requests

from dramatiq.brokers.redis import RedisBroker
from utils.logger import get_logger

redis_broker = RedisBroker(host="192.168.68.115", namespace='test1')
set_broker(redis_broker)

log = get_logger()

@actor
def count_words(url):
    # log.info('going to sleep........ zzzz......')
    sleep(5)
    # log.info('whoops awake, checking url!')
    response = requests.get(url)
    count = len(response.text.split(" "))
    count_words.logger.info(f"There are {count} words at {url!r}.")

