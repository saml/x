# -*- coding:utf-8 -*-
"""
Postgres commit timeout
"""
import logging

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
import sqlalchemy.engine.url
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, Integer

from toxiproxy import ToxiProxy

Base = declarative_base()
Session = None
_log = logging.getLogger(__name__)


# def connect():
#     return psycopg2.connect(
#         'dbname=postgres user=postgres password=postgres host=localhost port=5432 client_encoding=utf8'
#     )

def init_db(port=5434):
    _log.info('connecting to db port=%s', port)
    url = sqlalchemy.engine.url.URL(
        'postgresql',
        username='postgres',
        password='postgres',
        host='localhost',
        port=port,
        database='postgres',
    )
    engine = sqlalchemy.create_engine(
        url,
        echo='debug',
        echo_pool=True,
        client_encoding='utf8',
        use_native_unicode=True,
    )

    global Session
    Session = scoped_session(session_factory=sessionmaker())
    Session.configure(bind=engine)
    return engine


class Foo(Base):
    __tablename__ = 'foo'
    id = Column(Integer, primary_key=True)


def write():
    foo = Foo(id=1)
    Session.add(foo)
    _log.info('committing %s', foo)
    Session.commit()

def test():
    logging.basicConfig(level='DEBUG')
    init_db()

    foo = Foo(id=1)
    Session.add(foo)

    proxy = ToxiProxy(
        listen_addr=':5434',
        upstream_addr='localhost:5432',
        proxy_name='postgres',
    )
    proxy.setup(ignore_error=True)
    proxy.add()

    _log.info('committing %s', foo)
    Session.commit()


    # write()


if __name__ == '__main__':
    test()
