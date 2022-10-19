import concurrent.futures
import logging
import os
import time

import pika

_log = logging.getLogger(__name__)

QUEUE_NAME = "test"
HEARTBEAT = 2


def callback(channel, method, properties, body):
    _log.info(" [x] Received %s", body)
    time.sleep((HEARTBEAT + 1) * 2)


def connect(
    host="localhost",
    virtual_host="/",
    username="guest",
    password="guest",
    heartbeat=HEARTBEAT,
):
    param = pika.ConnectionParameters(
        host=host,
        virtual_host=virtual_host,
        credentials=pika.PlainCredentials(username=username, password=password),
        heartbeat=heartbeat,
    )
    return pika.BlockingConnection(parameters=param)


class ThreadExec:
    def __init__(self, conn, callback, executor):
        self.conn = conn
        self.callback = callback
        self.executor = executor

    def on_message_callback(self, channel, method, properties, body):
        future = self.executor.submit(
            lambda: self.callback(channel, method, properties, body)
        )
        future_timeout = HEARTBEAT / 2.0 if HEARTBEAT > 0 else None
        while True:
            try:
                result = future.result(future_timeout)
                _log.info(" ack")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return result
            except concurrent.futures.TimeoutError:
                _log.info("Future is not finished")
            finally:
                self.conn.process_data_events()


def main():
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "info").upper(),
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    )
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    with connect() as conn:
        thread_exec = ThreadExec(conn=conn, callback=callback, executor=executor)
        with conn.channel() as chan:
            chan.queue_declare(queue=QUEUE_NAME, durable=True)
            chan.basic_consume(
                queue=QUEUE_NAME, on_message_callback=thread_exec.on_message_callback
            )
            chan.start_consuming()


if __name__ == "__main__":
    main()
