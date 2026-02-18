from rq import Queue
from redis import Redis

redis_conn = Redis(host="localhost", port=6379)
queue = Queue("default", connection=redis_conn)
