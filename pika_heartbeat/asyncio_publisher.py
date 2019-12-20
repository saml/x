import asyncio
import logging
import os
import time

import aioamqp

_log = logging.getLogger(__name__)

QUEUE_NAME = "test"
HEARTBEAT = 2


async def send():
    transport, protocol = await aioamqp.connect(heartbeat=HEARTBEAT)
    channel = await protocol.channel()

    await channel.queue_declare(queue_name=QUEUE_NAME, durable=True)

    await channel.basic_publish(
        payload="Hello World!", exchange_name="", routing_key=QUEUE_NAME
    )

    _log.info(" [x] Sent 'Hello World!'")
    time.sleep((HEARTBEAT + 1) * 2)  # simulating idle time.

    _log.info(" [ ] Sending second message")
    await channel.basic_publish(
        payload="Hello World!", exchange_name="", routing_key=QUEUE_NAME
    )

    await protocol.close()
    transport.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "info").upper(),
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    )
    asyncio.get_event_loop().run_until_complete(send())
