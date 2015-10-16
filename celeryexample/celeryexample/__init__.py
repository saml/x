import logging

from .tasks import app
# default log. only need to configure this, not task logger(s).
log = app.log.get_default_logger()

def configure_logging(logger=log):
    log_level = logging.INFO

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.setLevel(log_level)

