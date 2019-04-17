# -*- coding:utf-8 -*-
import json
import time
import logging

import pika
from pika.adapters.blocking_connection import BlockingChannel
from timeout_decorator import timeout, TimeoutError


_log = logging.getLogger(__name__)

def connect():
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost',
            virtual_host='/',
            credentials=pika.PlainCredentials(
                username='guest',
                password='guest',
            ),
            socket_timeout=0.1,
            blocked_connection_timeout=0.1,
            connection_attempts=1,
            retry_delay=0.0,
            stack_timeout=0.2,
            port=5670,
        )
    )


def _publish(channel: BlockingChannel, message_number: int, mandatory=False):
    _log.info('publishing message %s', message_number)
    properties = pika.BasicProperties(
        content_type='application/json',
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
    )
    channel.basic_publish(
        exchange='',
        routing_key='myqueue',
        properties=properties,
        mandatory=mandatory,
        body=json.dumps({'some': message_number}),
    )


def publish(channel: BlockingChannel, message_number: int, timeout_secs: float = 1.0):
    try:
        timeout(timeout_secs)(_publish)(channel, message_number)
    except TimeoutError:
        _log.exception('Timed out (%s)', timeout_secs)
        channel.close()

if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    c = connect()
    ch = c.channel()
    ch.confirm_delivery()
    i = 0
    while True:
        i += 1
        publish(ch, i)
        time.sleep(1)
