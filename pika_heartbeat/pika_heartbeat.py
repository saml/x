import argparse
import logging
import threading
import time

import pika

DEFAULT_HEARTBEAT_SECS = 10
_log = logging.getLogger(__name__)


class Connection:
    def __init__(
        self,
        host="localhost",
        virtual_host="/",
        username="guest",
        password="guest",
        heartbeat=DEFAULT_HEARTBEAT_SECS,
    ):
        self.param = pika.ConnectionParameters(
            host=host,
            virtual_host=virtual_host,
            credentials=pika.PlainCredentials(username=username, password=password),
            heartbeat=heartbeat,
        )
        self.running = False
        self.ping_thread = None
        self.conn = None

    def stop(self):
        self.running = False

    def connect(self):
        self.conn = pika.BlockingConnection(parameters=self.param)

        # Attempts to keep using the connection in separate thread.
        self.ping_thread = threading.Thread(
            target=self.ping_connection, args=(self.conn,)
        )
        self.ping_thread.start()
        return self.conn

    def ping_connection(self, conn):
        _log.info("Start pinging connection")
        self.running = True
        while self.running:
            conn.add_callback_threadsafe(lambda: conn.sleep(0))
            time.sleep(2)


def main():
    logging.basicConfig(
        level="DEBUG", format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--heartbeat", type=int, default=DEFAULT_HEARTBEAT_SECS)
    args = parser.parse_args()
    heartbeat_secs = args.heartbeat
    consumer = Connection(heartbeat=heartbeat_secs)
    consumer_channel = consumer.connect().channel()

    def handle_message(*args, **kwargs):
        _log.info("Got message. Sleeping")
        time.sleep(60)

    try:
        consumer_channel.basic_consume("test", handle_message, auto_ack=True)
        consumer_channel.start_consuming()
    except KeyboardInterrupt:
        consumer_channel.stop_consuming()
        consumer.stop()
    finally:
        consumer.conn.close()
        consumer.ping_thread.join()


if __name__ == "__main__":
    main()
