import argparse
import logging
import time
import threading

import pika

from repeated_timer import RepeatedTimer

DEFAULT_HEARTBEAT_SECS = 60


def connect(
    host="localhost",
    virtual_host="/",
    username='guest',
    password='guest',
    heartbeat=DEFAULT_HEARTBEAT_SECS,
):
    param = pika.ConnectionParameters(
        host=host,
        virtual_host=virtual_host,
        credentials=pika.PlainCredentials(username=username, password=password),
        heartbeat=heartbeat,
    )
    return pika.BlockingConnection(parameters=param)

def rabbit_sleep(lock, connection):
    """
        This is used to ensure that we are sending heartbeats to rabbitMQ
    """
    if lock.acquire(timeout=0):
        try:
            connection.sleep(0)
        except:
            print("Error calling rabbit connection sleep")
        finally:
            lock.release()

def main():
    logging.basicConfig(
        level="DEBUG", format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    lock = threading.Lock()
    parser.add_argument("--heartbeat", type=int, default=DEFAULT_HEARTBEAT_SECS)
    parser.add_argument("--username", type=str, default='guest')
    parser.add_argument("--password", type=str, default='guest')
    args = parser.parse_args()
    heartbeat_secs = args.heartbeat
    sleep_secs = heartbeat_secs * 5  # sleep enough so that broker closes connection
    conn = connect(username=args.username, password=args.password, heartbeat=args.heartbeat)
    repeat_timer = RepeatedTimer(heartbeat_secs, rabbit_sleep, lock, conn)
    ch = conn.channel()
    lock.acquire()
    ch.basic_publish("", "test", "")
    lock.release()
    time.sleep(sleep_secs)
    lock.acquire()
    ch.basic_publish("", "test", "")  # this is expected to fail
    lock.release()


if __name__ == "__main__":
    main()
