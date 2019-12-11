import argparse
import logging

import pika

DEFAULT_HEARTBEAT_SECS = 10


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
    consumer = connect(heartbeat=heartbeat_secs)
    consumer_channel = consumer.channel()
    producer = connect(
        heartbeat=heartbeat_secs, virtual_host="foo"
    )  # Actually connects to different rabbitmq host
    producer_channel = producer.channel()

    def handle_message(*args, **kwargs):
        producer_channel.basic_publish("", "test-publish", "")

    try:
        consumer_channel.basic_consume("test", handle_message, auto_ack=True)
        consumer_channel.start_consuming()
    except KeyboardInterrupt:
        consumer_channel.start_consuming()
    finally:
        producer.close()
        consumer.close()


if __name__ == "__main__":
    main()
