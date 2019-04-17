# -*- coding:utf-8 -*-
import logging
import time

import kombu

_log = logging.getLogger(__name__)


def connect():
    conn = kombu.Connection('amqp://guest:guest@localhost:5670//', connect_timeout=0.1,
                            transport_options=dict(
                                confirm_publish=True,
                                read_timeout=1.0,
                                write_timeout=1.0,
                            ))
    chan = conn.channel()
    return kombu.Producer(chan)


def publish(producer, message_number):
    _log.info('publishing message %s', message_number)
    producer.publish({'a': message_number}, routing_key='myqueue')


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    c = connect()
    i = 0
    while True:
        i += 1
        publish(c, i)
        time.sleep(1)
