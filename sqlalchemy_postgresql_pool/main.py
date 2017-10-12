'''sqlalchemy postgres reconnecting pool'''

import time
import logging

import sqlalchemy
import sqlalchemy.engine.url
import sqlalchemy.pool
import sqlalchemy.exc
import sqlalchemy.event
import psycopg2

logger = logging.getLogger(__name__)

DEFAULT_URLS=(
    'postgresql://postgres:postgres@localhost:5454/postgres',
    'postgresql://postgres:postgres@localhost:5455/postgres',
)


class Psycopg2Pool:
    '''Connects to one of given urls.'''
    def __init__(self, urls):
        self.urls = [sqlalchemy.engine.url.make_url(url) for url in urls]

    def __call__(self, *args, **kwargs):
        for url in self.urls:
            try:
                logger.info('connecting to %s', url)
                return psycopg2.connect(
                    user=url.username,
                    password=url.password,
                    host=url.host,
                    port=url.port,
                    dbname=url.database
                )
            except:
                logger.exception('')


def ping_connection(connection, branch):
    '''manual connection ping.
    This is until 1.2.0 is released,
    which includes pool_pre_ping=True argument in create_engine.

    copied from http://docs.sqlalchemy.org/en/latest/core/pooling.html#custom-legacy-pessimistic-ping
    '''
    if branch:
        return
    original_should_close = connection.should_close_with_result
    connection.should_close_with_result = False
    try:
        connection.scalar(sqlalchemy.select([1]))
    except sqlalchemy.exc.DBAPIError as err:
        if err.connection_invalidated:
            connection.scalar(sqlalchemy.select([1]))
        else:
            raise
    finally:
        connection.should_close_with_result = original_should_close


def start(engine):
    '''main loop. makes db query in a loop'''
    while True:
        with engine.connect() as conn:
            logger.info('conn=%s', conn)
            for row in conn.execute(sqlalchemy.select([1])):
                logger.info(row)
        time.sleep(1)

def create_engine(urls=DEFAULT_URLS):
    '''reconnecting pool for sqlalchemy 1.2.0.'''
    get_connection = Psycopg2Pool(urls)
    return sqlalchemy.create_engine('postgresql://', creator=get_connection, pool_pre_ping=True, echo=True)

def create_engine_old(urls=DEFAULT_URLS):
    '''reconnecting pool for sqlalchemy 1.1.x'''
    get_connection = Psycopg2Pool(urls)
    engine = sqlalchemy.create_engine('postgresql://', creator=get_connection, echo=True)
    sqlalchemy.event.listen(engine, 'engine_connect', ping_connection)
    return engine

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    engine = create_engine_old()
    start(engine)
