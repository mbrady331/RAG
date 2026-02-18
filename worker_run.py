# Run main.py first in terminal and then run worker_run.py in a separate terminal instance.

from client.rq_client import queue
from rq.worker import SimpleWorker

if __name__ == "__main__":
    worker = SimpleWorker([queue], connection=queue.connection)
    worker.work()
