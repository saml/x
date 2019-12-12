import threading
import time
import os
import logging

_log = logging.getLogger(__name__)


def target():
    while True:
        _log.info("Thread is doing something")
        time.sleep(10)


def main():
    t = threading.Thread(target=target)
    t.start()
    t.join(0.1)
    _log.info("Thread is joined")


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "info").upper(),
        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    )
    main()
