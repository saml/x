#!/usr/bin/env python

import argparse
import re
import os
try:
    from urllib.parse import unquote_plus
except ImportError:
    from urllib import unquote_plus

import requests

URL_IN_HTML = re.compile(r'"?(https?://[^"\s]+)["\s]?')
VIDEO_URL = re.compile(r'"?(https?://[^"\s]+\.mp4)["\s]?')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'
}

def to_player_url(url_or_html):
    m = URL_IN_HTML.search(url_or_html)
    if m:
        url = m.group(1)
        if '/embed/' not in url:
            return os.path.join(url, 'player/cvp')
        return url
    return ''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url_or_html')
    args = parser.parse_args()
    url = to_player_url(args.url_or_html)
    #html = unquote_plus(requests.get(url).text)
    resp = requests.get(url, headers=HEADERS)
    html = unquote_plus(resp.text)
    videos = set()
    print(html)
    print(resp.url)
    for x in VIDEO_URL.finditer(html):
        videos.add(x.group(1))
    print(videos)
