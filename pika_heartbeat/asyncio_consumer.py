import asyncio
import logging
import time
import os

import aioamqp

_log = logging.getLogger(__name__)

QUEUE_NAME = "test"
HEARTBEAT = 2


async def callback(channel, body, envelope, properties):
    _log.info(" [x] Received %s", body)
    time.sleep((HEARTBEAT + 1) * 3)
    _log.info(" ack")
    await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)


async def receive():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()

    await channel.queue_declare(queue_name=QUEUE_NAME, durable=True)
    await channel.basic_qos(prefetch_count=1, prefetch_size=0, connection_global=False)

    await channel.basic_consume(callback, queue_name=QUEUE_NAME)


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "info").upper(),
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    )

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(receive())
    event_loop.run_forever()
