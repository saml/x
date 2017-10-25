'''
https://www.postgresql.org/docs/current/static/libpq-connect.html#libpq-multiple-hosts
'''
from contextlib import contextmanager

import psycopg2
import sqlalchemy
import sqlalchemy.engine.url
import sqlalchemy.orm
import sqlalchemy.exc

Session = session_factory = sqlalchemy.orm.sessionmaker()


def creator_lib10():
    return psycopg2.connect(
        'user=postgres password=postgres host=localhost,localhost port=5454,5455 dbname=postgres connect_timeout=3')


def creator_manual_loop():
    connection_strs = (
        'user=postgres password=postgres host=localhost port=5454 dbname=postgres connect_timeout=3',
        'user=postgres password=postgres host=localhost port=5455 dbname=postgres connect_timeout=3',
    )
    for connection_str in connection_strs:
        try:
            return psycopg2.connect(connection_str)
        except psycopg2.Error as err:
            print(err)


@contextmanager
def new_session():
    sess = Session()
    yield sess
    sess.close()


if __name__ == '__main__':
    engine = sqlalchemy.create_engine('postgres://', creator=creator_manual_loop, echo=True)
    Session.configure(bind=engine)
    while True:
        try:
            input('Press Enter key to ping db: ')
            with new_session() as session:
                result = session.execute(sqlalchemy.select([1])).scalar()
                print('DB ping: {}'.format(result))
        except KeyboardInterrupt:
            break
        except sqlalchemy.exc.SQLAlchemyError as err:
            print(err)
    print('Bye')
