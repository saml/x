# -*- coding:utf-8 -*-
"""
Postgres commit timeout
"""
import logging
import socket
import struct
import ctypes
import ctypes.util

import psycopg2

from toxiproxy import ToxiProxy

_log = logging.getLogger(__name__)


def connect(port=5434, timeout_secs=2):
    conn = psycopg2.connect(f'dbname=postgres user=postgres password=postgres host=localhost port={port} client_encoding=utf8')
    fileno = conn.fileno()
    _log.info('getting socket from file descriptor: %s', fileno)
    sock = socket.socket(fileno=fileno, proto=4, family=socket.AF_INET, type=socket.SOCK_STREAM)
    # libc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))
    # for opt in (socket.SO_RCVTIMEO, socket.SO_SNDTIMEO):
    #     # timeout = struct.pack('ll', int(timeout_secs), 0)
    #     ret = libc.setsockopt(fileno, socket.SOL_SOCKET, opt, ctypes.c_void_p(timeout_secs), ctypes.c_int(0))
    #     _log.info('Set timeout (%s) on socket %s returned: %s', opt, fileno, ret)
    #     if ret != 0:
    #         _log.error('errono: %s', ctypes.get_errno())
    #         raise Exception("Wrong usage of setsockopt")
    # libc.setsockopt()
    # _sock = socket.fromfd(fileno, socket.AF_INET, socket.SOCK_STREAM)
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, _sock=_sock)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    for opt in (socket.SO_RCVTIMEO, socket.SO_SNDTIMEO):
        timeout = struct.pack('ll', int(timeout_secs), 0)
        sock.setsockopt(socket.SOL_SOCKET, opt, timeout)
    _log.info('Set timeout on socket: %s', sock)

    return conn


def test():
    logging.basicConfig(level='DEBUG')
    proxy = ToxiProxy(
        listen_addr=':5434',
        upstream_addr='localhost:5432',
        proxy_name='postgres',
    )
    proxy.setup(ignore_error=True)
    proxy.remove()
    _log.info('connecting to postgres')
    conn = connect()
    with conn.cursor() as curs:
        curs.execute('insert into foo(id) values (1)')
        try:
            _log.info('committing')
            proxy.add()
            conn.commit()
        except TimeoutError:
            _log.exception('failed to commit')
            conn.rollback()


if __name__ == '__main__':
    test()
