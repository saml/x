import random
import functools
import time

from celery import Celery, Task
from celery.exceptions import SoftTimeLimitExceeded, MaxRetriesExceededError
import celery.signals
from eliot import start_action, add_destinations, to_file, Action, Message

to_file(open('a.log', 'wb'))
add_destinations(print)
app = Celery(__name__)


@celery.signals.setup_logging.connect()
def _setup_logging(*args, **kwargs):
    pass


class TaskFailure(Exception):
    """
    Custom exception to raise to request retry.
    """


class CeleryTask(Task):
    def __call__(self, *args, **kwargs):
        try:
            try:
                super().__call__(*args, **kwargs)
            except SoftTimeLimitExceeded:
                self.on_timeout(self, *args, **kwargs)
                self.retry(countdown=0)
            except TaskFailure:
                self.retry(countdown=1 + self.request.retries)
        except MaxRetriesExceededError:
            self.on_max_retries_exceeded(*args, **kwargs)
            raise

    def on_max_retries_exceeded(self, *args, **kwargs):
        """
        Meh
        """

    def on_timeout(self, *args, **kwargs):
        """
        Meh
        """


def task(timeout_secs=None, max_retries_func=None, *args_task, **kwargs_task):
    def deco(func):
        @app.task(bind=True, acks_late=True, soft_time_limit=timeout_secs, retry_backoff=True,
                  retry_backoff_max=100, *args_task, **kwargs_task)
        @functools.wraps(func)
        def _task(self, *args, **kwargs):
            try:
                try:
                    func(*args, **kwargs)
                except SoftTimeLimitExceeded:
                    self.retry(countdown=0)
                except TaskFailure:
                    self.retry(countdown=1 + self.request.retries)
            except MaxRetriesExceededError:
                if max_retries_func is not None:
                    max_retries_func(*args, **kwargs)
                raise

        return _task

    return deco


def random_bool():
    return random.choice((True, False))


def do_random():
    should_fail = random_bool()
    if should_fail:
        1 / 0
    should_retry = random_bool()
    if should_retry:
        raise TaskFailure()
    should_run_forever = random_bool()
    if should_run_forever:
        while True:
            time.sleep(10)


@app.task(base=CeleryTask)
def second_task(action_id):
    Message.log(action_id=action_id)
    with Action.continue_task(task_id=action_id):
        Message.log(action_id=action_id, ty=str(type(action_id)))
        # do_random()


@app.task(base=CeleryTask)
def my_task():
    with start_action(action_type='main') as action:
        second_task.delay('{}'.format(action.serialize_task_id()))
