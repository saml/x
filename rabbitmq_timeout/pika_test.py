# -*- coding:utf-8 -*-
"""
Test case for implementing timeout on pika (RabbitMQ).
"""

import logging

# import sanic
# import sanic.response
import pika
import pika.channel
import pika.spec
import attr

DEFAULT_CONNECTION_PARAMS = pika.ConnectionParameters(
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
DELAY_SECS = 1.0

_log = logging.getLogger(__name__)


# app = sanic.Sanic()
#
#
# @app.route('/')
# async def index(request):
#     return sanic.response.json({'a': 'b'})


@attr.s
class Client:
    params: pika.ConnectionParameters = DEFAULT_CONNECTION_PARAMS
    connection: pika.SelectConnection = None
    channel: pika.channel.Channel = None

    def run(self):
        self.connection = self.connect()
        self.connection.ioloop.start()

    def connect(self):
        return pika.SelectConnection(
            self.params,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_close,
        )

    def open_channel(self):
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        _log.info('Channel opened: %s', channel)
        self.channel = channel
        self.channel.add_on_close_callback(self.on_channel_close)
        self.channel.confirm_delivery(self.on_confirm_delivery)
        self.publish()

    def on_confirm_delivery(self, method_frame):
        _log.info('Confirm delivery: %s', method_frame)
        # If this call is delayed due to server latency,
        # How do I fail the basic_publish?

    def on_channel_close(self, channel, reason):
        _log.info('Channel closed: %s (%s)', channel, reason)
        self.connection.close()

    def on_connection_open(self, connection):
        _log.info('Connection open: %s', connection)
        self.open_channel()

    def on_connection_open_error(self, connection: pika.SelectConnection, err):
        _log.error('Error opening connection: %s (%s)', connection, err)
        self.connection.ioloop.call_later(DELAY_SECS, self.connection.ioloop.stop)

    def on_connection_close(self, connection, reason):
        _log.info('Connection closed: %s (%s)', connection, reason)
        self.connection.ioloop.call_later(DELAY_SECS, self.connection.ioloop.stop)

    def publish(self):
        _log.info('Publishing message')
        properties = pika.BasicProperties(
            content_type='application/json',
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
        )
        self.channel.basic_publish('', 'myqueue', '{}', properties)
        self.connection.ioloop.call_later(DELAY_SECS, self.publish)


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    c = Client()
    c.run()
    # app.run(host='0.0.0.0', port=8000)
