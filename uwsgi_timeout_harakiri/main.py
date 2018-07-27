# -*- coding:utf-8 -*-
"""
a WSGI app
"""

import falcon

_sleeps = [0] * 9
_sleeps.append(3)


class Slow:
    """
    Slow response
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response):
        """
        GET /
        """
        import time
        import random

        # time.sleep(random.choice(_sleeps))
        time.sleep(30)
        resp.status = falcon.HTTP_200
        resp.media = {
            'method': req.method,
            'url': req.url,
        }


class Fast:
    """
    Fast
    """

    def on_get(self, req: falcon.Request, resp: falcon.Response):
        resp.status = falcon.HTTP_200
        resp.media = {
            'method': req.method,
            'url': req.url,
        }


def create_app():
    app = falcon.API()
    app.add_route('/', Slow())
    app.add_route('/fast', Fast())
    return app


app = create_app()
