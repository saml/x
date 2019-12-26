import logging
import os
import queue
import threading
import time

import pika
import pika.exceptions

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


class Publisher:
    def __init__(self, connect_func):
        self.connect = connect_func
        self.quit = None
        self.queue = None
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self._thread_start)
        self.thread.start()
        self.thread.join(0)

    def publish(self, exchange, routing_key, body, properties=None, mandatory=False):
        _log.info("Enqueue to publish")
        self.queue.put(
            dict(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=properties,
                mandatory=mandatory,
            )
        )

    def _publish_loop(self):
        with self.connect() as connection:
            with connection.channel() as channel:
                while not self.quit.is_set():
                    try:
                        connection.process_data_events()  # This makes connection alive
                        kwargs = self.queue.get(block=True, timeout=1.0)
                        _log.info("Publishing")
                        channel.basic_publish(**kwargs)
                    except queue.Empty:
                        _log.info("Nothing to publish")

    def _thread_start(self):
        self.queue = queue.Queue()
        self.quit = threading.Event()
        while not self.quit.is_set():
            try:
                self._publish_loop()
            except pika.exceptions.AMQPError as err:
                _log.error("Pika error. Will reconnect", exc_info=err)


def main():
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "info").upper(),
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    )
    publisher = Publisher(connect)
    publisher.start()
    for x in range(10):
        _log.info("Sending first message and sleeping")
        publisher.publish(
            exchange="", routing_key=QUEUE_NAME, body="Hello", mandatory=True,
        )
        time.sleep((HEARTBEAT + 1) * 3)
        _log.info("Sending second message")
        publisher.publish(
            exchange="", routing_key=QUEUE_NAME, body="Hello",
        )
    publisher.quit.set()


if __name__ == "__main__":
    main()
