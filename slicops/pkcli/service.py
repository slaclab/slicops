"""Start SlicOps services.

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.pkcli
import tornado.httpclient
import tornado.web


class Commands(slicops.pkcli.CommandsBase):

    def ui_api(self, tcp_port=None, prod=False):
        """Start UI API web server.

        This web server provides a friendly and secure API for SlicOps apps.

        Args:
            prod (bool): run in production mode (serve Vue statically)

        """
        from pykern import pkconfig, pkresource
        from pykern.api import server
        from slicops import config, ui_api, quest
        from tornado import web

        def _tcp_port():
            return PKDict(tcp_port=pkconfig.parse_positive_int(tcp_port)) if tcp_port else PKDict()

        def _uri_map(config):
            if prod:
                return [
                    (
                        # very specific so we control the name space
                        r"^(?:/screen/?|/)(assets/\w+.\w+\.(?:css|js)|favicon.png|)$",
                        web.StaticFileHandler,
                        PKDict(
                            path=str(pkresource.file_path("vue")),
                            default_filename="index.html",
                        ),
                    ),
                ]
            return [
                (
                    # send any non-api call to the proxy
                    rf"^(?!{config.api_uri}).*",
                    ProxyHandler,
                    PKDict(
                        proxy_url=f"http://localhost:{config.vue_port}",
                    ),
                ),
            ]

        c = config.cfg().ui_api.copy()
        server.start(
            attr_classes=quest.attr_classes(),
            api_classes=ui_api.api_classes(),
            http_config=c.pkupdate(PKDict(
                uri_map=_uri_map(c),
                **_tcp_port(),
            ))
        )


class ProxyHandler(tornado.web.RequestHandler):
    def initialize(self, proxy_url, **kwargs):
        super(ProxyHandler, self).initialize(**kwargs)
        self.http_client = tornado.httpclient.AsyncHTTPClient()
        self.proxy_url = proxy_url

    async def get(self):
        r = await self.http_client.fetch(f"{self.proxy_url}{self.request.uri}")
        self.set_status(r.code)
        self.set_header("Content-Type", r.headers["Content-Type"])
        self.write(r.body)
