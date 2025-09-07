import os
from redis import Redis
from rq import Worker, Queue, Connection

listen = ['default']
redis_conn = Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
