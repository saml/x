
from celery.utils.log import get_task_logger
from celery import Celery

app = Celery(__name__, broker='amqp://localhost:5672//')
log = get_task_logger(__name__) # task logger, not default logger.

@app.task
def add_one(x):
    log.info('Got x = %s', x)
    return x + 1


