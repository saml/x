# -*- coding:utf-8 -*-
from typing import List
import argparse

import attr
import requests


@attr.s(auto_attribs=True)
class ToxiProxy:
    url: str = 'http://localhost:8474'
    listen_addr: str = ':5670'
    upstream_addr: str = 'localhost:5672'
    proxy_name: str = 'rabbitmq'
    toxic_names: List[str] = []

    def all_toxics(self):
        return requests.get(self.url + f'/proxies/{self.proxy_name}/toxics').json()

    def setup(self, ignore_error=False):
        resp = requests.post(self.url + '/proxies',
                             json=dict(
                                 name=self.proxy_name,
                                 listen=self.listen_addr,
                                 upstream=self.upstream_addr,
                             ))
        if not ignore_error:
            resp.raise_for_status()
        self.toxic_names = [d['name'] for d in self.all_toxics()]

    def add_latency(self, latency_msec):
        toxic_name = 'latency_downstream'
        requests.post(self.url + f'/proxies/{self.proxy_name}/toxics',
                      json=dict(
                          name=toxic_name,
                          type='latency',
                          stream='downstream',
                          attributes=dict(
                              latency=latency_msec,
                          ),
                      )).raise_for_status()
        self.toxic_names.append(toxic_name)

    def add_bandwidth(self, rate_kbps):
        toxic_name = 'bandwidth_downstream'
        requests.post(self.url + f'/proxies/{self.proxy_name}/toxics',
                      json=dict(
                          name=toxic_name,
                          type='bandwidth',
                          stream='downstream',
                          attributes=dict(
                              rate=rate_kbps,
                          ),
                      )).raise_for_status()
        self.toxic_names.append(toxic_name)

    def add(self, latency_msec=10000, rate_kbps=1):
        self.add_latency(latency_msec)
        self.add_bandwidth(rate_kbps)

    def remove(self):
        toxic_names = self.toxic_names[:]
        for toxic_name in toxic_names:
            resp = requests.delete(self.url + f'/proxies/{self.proxy_name}/toxics/{toxic_name}')
            if resp.status_code not in (200, 204, 404):
                resp.raise_for_status()
        self.toxic_names = []


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--listen', default=':5670')
    parser.add_argument('--upstream', default='localhost:5672')
    parser.add_argument('--proxy', default='http://localhost:8474')

    subparsers = parser.add_subparsers(dest='action')
    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('--latency', type=int, default=10000)
    parser_add.add_argument('--rate', type=int, default=1)
    parser_add.add_argument('name')

    parser_remove = subparsers.add_parser('remove')
    parser_remove.add_argument('name')

    args = parser.parse_args()

    proxy = ToxiProxy(
        url=args.proxy,
        proxy_name=args.name,
        listen_addr=args.listen,
        upstream_addr=args.upstream,
    )
    proxy.setup(ignore_error=True)
    if args.action == 'add':
        proxy.add(latency_msec=args.latency, rate_kbps=args.rate)
    elif args.action == 'remove':
        proxy.remove()
