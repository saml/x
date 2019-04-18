# -*- coding:utf-8 -*-
import json
import time
import logging

import pika
from pika.adapters.blocking_connection import BlockingChannel

from toxiproxy import ToxiProxy

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
            tcp_options={
                # socket.SO_RCVTIMEO: 1.0,
                # socket.SO_SNDTIMEO: 1.0,
                'TCP_READTIMEOUT': 1.0,
                'TCP_WRITETIMEOUT': 1.0,
            },
        )
    )


def publish(channel: BlockingChannel, message_number: int, mandatory=False, exchange=''):
    _log.info('publishing message %s', message_number)
    properties = pika.BasicProperties(
        content_type='application/json',
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
    )
    channel.basic_publish(
        exchange=exchange,
        routing_key='myqueue',
        properties=properties,
        mandatory=mandatory,
        body=json.dumps({'some': message_number}),
    )


def test():
    proxy = ToxiProxy()
    proxy.setup(ignore_error=True)

    c = connect()
    ch = c.channel()
    ch.confirm_delivery()

    proxy.add()
    try:
        publish(ch, 1)
    except KeyboardInterrupt:
        proxy.remove()
        ch.close()
    c.close()



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
