import argparse
import logging
import threading
import time
import functools
import os
from queue import Queue

import pika

DEFAULT_HEARTBEAT_SECS = 5
_log = logging.getLogger(__name__)


def connect(
    host="localhost",
    virtual_host="/",
    username="guest",
    password="guest",
    heartbeat=DEFAULT_HEARTBEAT_SECS,
):
    param = pika.ConnectionParameters(
        host=host,
        virtual_host=virtual_host,
        credentials=pika.PlainCredentials(username=username, password=password),
        heartbeat=heartbeat,
    )
    return pika.BlockingConnection(parameters=param)


class Consumer:
    def __init__(self, conn):
        self.conn = conn
        self.q = None
        self.worker_thread = None

    def stop(self):
        _log.info("Stopping consumer")
        if self.q is None:
            _log.info("Not yet started. Nothing to stop")
            return

        while not self.q.empty():
            item = self.q.get()
            _log.info("Draining work queue: %s", item)
            self.q.task_done()
        _log.info("Drained worked queue")
        self.q.put(None)  # signal worker to break out of loop

        if self.worker_thread is not None:
            _log.info("Joining worker thread")
            # Let the last work to finish
            self.worker_thread.join(timeout=100.0)  # timeout in seconds
        _log.info("Joining work queue")
        self.q.join()
        if self.conn is not None:
            _log.info("Closing connection")
            self.conn.close()

    def start_consuming(self, queue_name, handler):
        self.q = Queue()

        def worker():
            while True:
                item = self.q.get()
                _log.info("Worker got item: %s", item)
                if item is None:
                    _log.info("Got signal to break out of loop")
                    self.q.task_done()
                    break

                channel, method, properties, body = item
                handler(channel, method, properties, body)
                _log.info("Work is done. Ack: %s", method.delivery_tag)
                self.conn.add_callback_threadsafe(
                    functools.partial(
                        channel.basic_ack, delivery_tag=method.delivery_tag
                    )
                )
                self.q.task_done()

        def message_handler(channel, method, properties, body):
            _log.info("Enqueueing work")
            self.q.put((channel, method, properties, body))

        _log.info("Starting worker thread")
        self.worker_thread = threading.Thread(target=worker)
        self.worker_thread.start()
        self.worker_thread.join(timeout=0.1)

        _log.info("Starting consumer")
        with self.conn.channel() as channel:
            channel.basic_consume(
                queue=queue_name, on_message_callback=message_handler, auto_ack=False
            )
            channel.start_consuming()


def main():
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "info").upper(),
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    )
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--heartbeat", type=int, default=DEFAULT_HEARTBEAT_SECS)
    args = parser.parse_args()
    heartbeat_secs = args.heartbeat
    conn = connect(heartbeat=heartbeat_secs)
    consumer = Consumer(conn)

    def handle_message(*args, **kwargs):
        _log.info("Handling a message takes longer than heartbeat")
        time.sleep(30)

    try:
        consumer.start_consuming("test", handle_message)
    finally:
        try:
            consumer.stop()
        except Exception:
            _log.exception("Bye")


if __name__ == "__main__":
    main()
