# -*- coding:utf-8 -*-
import kombu


def connect():
    conn = kombu.Connection('amqp://guest:guest@localhost:5670//', connect_timeout=0.1, transport_options={'confirm_publish': True})
    chan = conn.channel()
    return kombu.Producer(chan)


def publish(producer):
    producer.publish({'a': 'b'}, routing_key='myqueue')
