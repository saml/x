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
import psycopg2.extensions
import psycopg2.extras

from toxiproxy import ToxiProxy

_log = logging.getLogger(__name__)


class TimeVal(ctypes.Structure):
    _fields_ = [('a', ctypes.c_int), ('b', ctypes.c_int)]


def _connect(port=5434, timeout_secs=2):
    conn = psycopg2.connect(f'dbname=postgres user=postgres password=postgres host=localhost port={port} client_encoding=utf8')
    fileno = conn.fileno()
    _log.info('getting socket from file descriptor: %s', fileno)
    # sock = socket.socket(fileno=fileno, proto=4, family=socket.AF_INET, type=socket.SOCK_STREAM)
    libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
    libc.__errno_location.restype = ctypes.POINTER(ctypes.c_int)

    for opt in (socket.SO_RCVTIMEO, socket.SO_SNDTIMEO):
        # timeout = struct.pack('ll', int(timeout_secs), 0)
        timeout = TimeVal(int(timeout_secs), 0)
        ret = libc.setsockopt(ctypes.c_int(fileno),
                              ctypes.c_int(socket.SOL_SOCKET),
                              ctypes.c_int(opt),
                              ctypes.byref(timeout),
                              ctypes.sizeof(timeout))
        _log.info('Set timeout (%s) on socket %s returned: %s', opt, fileno, ret)
        if ret != 0:
            errono = libc.__errno_location().contents.value
            _log.error('errono: %s', errono)
            raise Exception(f'Wrong usage of setsockopt. errono={errono}')
    # libc.setsockopt()
    # _sock = socket.fromfd(fileno, socket.AF_INET, socket.SOCK_STREAM)
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, _sock=_sock)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    # for opt in (socket.SO_RCVTIMEO, socket.SO_SNDTIMEO):
    #     timeout = struct.pack('ll', int(timeout_secs), 0)
    #     sock.setsockopt(socket.SOL_SOCKET, opt, timeout)
    # _log.info('Set timeout on socket: %s', sock)

    return conn


def connect(port=5434, timeout_secs=2):
    # psycopg2.extensions.set_wait_callback(psycopg2.extras.wait_select)
    conn = psycopg2.connect(f'dbname=postgres user=postgres password=postgres host=localhost port={port} client_encoding=utf8')
    return conn


def test():
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
        except (TimeoutError, KeyboardInterrupt):
            _log.exception('failed to commit')
            conn.rollback()


def test_no_proxy():
    proxy = ToxiProxy(
        listen_addr=':5434',
        upstream_addr='localhost:5432',
        proxy_name='postgres',
    )
    proxy.setup(ignore_error=True)
    proxy.remove()
    conn = connect()
    with conn.cursor() as curs:
        curs.execute('insert into foo(id) values (1)')
        conn.commit()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    # test_no_proxy()
    test()
