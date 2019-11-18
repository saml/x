import argparse
import logging
import time

import pika

DEFAULT_HEARTBEAT_SECS = 60


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
    sleep_secs = heartbeat_secs * 5  # sleep enough so that broker closes connection
    conn = connect(heartbeat=args.heartbeat)
    ch = conn.channel()
    ch.basic_publish("", "test", "")
    time.sleep(sleep_secs)
    ch.basic_publish("", "test", "")  # this is expected to fail


if __name__ == "__main__":
    main()
