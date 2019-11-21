import argparse
import logging
import pika
import threading
import queue

from datetime import datetime

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


def consuming_thread(heartbeat_secs, q):
    consumer = connect(heartbeat=heartbeat_secs, virtual_host='/')
    consumer_channel = consumer.channel()

    def handle_message(*args, **kwargs):
        q.put('test-publish {}'.format(datetime.now()))

    try:
        # Note: auto_ack=True can result in lost messages
        consumer_channel.basic_consume('test', handle_message, auto_ack=True)
        consumer_channel.start_consuming()
    except KeyboardInterrupt:
        consumer_channel.start_consuming()
    finally:
        consumer.close()


def publishing_thread(heartbeat_secs, q):
    producer = connect(heartbeat=heartbeat_secs, virtual_host='/')
    producer_channel = producer.channel()

    running = True

    while running:
        producer.process_data_events()
        try:
            v = q.get(block=True, timeout=5)
            print('publishing: {}\n'.format(v))
            producer_channel.basic_publish('', 'test-two', v)
        except queue.Empty:
            print('nothing to publish!\n')
            pass

    consumer.close()


def main():
    logging.basicConfig(
        level='INFO', format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--heartbeat", type=int, default=DEFAULT_HEARTBEAT_SECS)
    args = parser.parse_args()
    heartbeat_secs = args.heartbeat

    q = queue.SimpleQueue()
    consuming_t = threading.Thread(target=consuming_thread, args=(heartbeat_secs, q))
    publishing_t = threading.Thread(target=publishing_thread, args=(heartbeat_secs, q))
    consuming_t.start()
    publishing_t.start()
    print('Waiting for threads to finish...')
    consuming_t.join()
    publishing_t.join()
    print('Exiting...')

if __name__ == "__main__":
    main()
