# -*- coding:utf-8 -*-
import logging
import json
import time

import amqp

_log = logging.getLogger(__name__)


def connect():
    return amqp.Connection(
        host='localhost:5670',
        virtual_host='/',
        userid='guest',
        password='guest',
        connect_timeout=1.0,
        # read_timeout=0.5,
        write_timeout=0.5,
        confirm_publish=True
    )


def publish(channel: amqp.Channel, message_number: int, mandatory=True):
    _log.info('publishing message %s', message_number)

    channel.basic_publish(
        amqp.Message(
            body=json.dumps({'pyamqp': message_number}),
            content_type='application/json',
            delivery_mode=2,
        ),
        exchange='',
        routing_key='myqueue',
        mandatory=mandatory,
        # timeout=2.0,
    )


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    c = connect()
    c.connect()
    ch = c.channel()
    i = 0
    while True:
        i += 1
        publish(ch, i)
        time.sleep(1)
