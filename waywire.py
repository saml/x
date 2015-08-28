#!/usr/bin/env python

import argparse
import re
import os
try:
    from urllib.parse import unquote_plus, urlparse
except ImportError:
    from urllib import unquote_plus
    from urlparse import urlparse

import requests

URL_IN_HTML = re.compile(r'"?(https?://[^"\s]+)["\s]?')
VIDEO_URL = re.compile(r'"?(https?://[^"\s]+\.mp4)["\s]?')
CID = re.compile(r'"clipId"\s*:\s*"([^"]+)"')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'
}
VIDEO_SIZE=re.compile(r'_(\d+)x(\d+)\.')

def to_player_url(url_or_html):
    m = URL_IN_HTML.search(url_or_html)
    if m:
        url = m.group(1)
        if '/embed/' not in url:
            return os.path.join(url, 'player/cvp')
        return url
    return ''

def fetch(url):
    print('FETCH ' + url)
    return requests.get(url, headers=HEADERS)

def find_cid(html):
    m = CID.search(html)
    if m:
        return m.group(1)

def base_url(url):
    p = urlparse(url)
    return '{}://{}'.format(p.scheme, p.netloc)

def video_size(url):
    m = VIDEO_SIZE.search(url)
    if m:
        return max(1, int(m.group(1), 10)) * max(1, int(m.group(2), 10))
    return 0

def fetch_embed_player(url):
    resp = fetch(url)
    html = unquote_plus(resp.text)
    cid = find_cid(html)
    if cid:
        # url was a redirect page, not actual video player.
        embed_url = '{}/embed/player/container/1920/922/?content={}&widget_type_cid=cvp'.format(base_url(url), cid)
        resp = fetch(embed_url)
        return unquote_plus(resp.text)
    return html

def find_videos(html):
    videos = {}
    for x in VIDEO_URL.finditer(html):
        video_url = x.group(1)
        videos[video_size(video_url)] = video_url
    return videos

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url_or_html')
    args = parser.parse_args()

    url = to_player_url(args.url_or_html)
    html = fetch_embed_player(url)
    videos = find_videos(html)
    print(videos)
