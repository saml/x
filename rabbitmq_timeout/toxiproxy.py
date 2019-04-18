# -*- coding:utf-8 -*-
from typing import List

import attr
import requests


@attr.s
class ToxiProxy:
    url: str = 'http://localhost:8474'
    listen_addr: str = ':5670'
    upstream_addr: str = 'localhost:5672'
    proxy_name: str = 'rabbitmq'
    toxic_names: List[str] = []

    def setup(self, ignore_error=False):
        resp = requests.post(self.url + '/proxies',
                             json=dict(
                                 name=self.proxy_name,
                                 listen=self.listen_addr,
                                 upstream=self.upstream_addr,
                             ))
        if not ignore_error:
            resp.raise_for_status()

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
