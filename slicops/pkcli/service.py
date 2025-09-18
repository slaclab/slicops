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
        from slicops import config, quest, sliclet, ui_api

        from tornado import web

        def _dev_uri_map(config):
            return [
                (
                    # send any non-api call to the proxy
                    rf"^(?!{config.api_uri}).*",
                    _ProxyHandler,
                    PKDict(
                        proxy_url=f"http://localhost:{config.vue_port}",
                    ),
                ),
            ]

        def _prod_uri_map(config):
            d = PKDict(
                # TODO(robnagler) package_path
                path=str(pkresource.file_path("vue")),
                default_filename="index.html",
            )
            return [
                # NOTE: StaticFileHandler requires match returns a group
                (
                    # very specific so we control the name space
                    r"^/(assets/[^/.]+\.(?:css|js)|favicon.png|index.html|)$",
                    web.StaticFileHandler,
                    d,
                ),
                (
                    # vue index.html is returned for sliclet URLs
                    rf"^/($|(?:{'|'.join(sliclet.names())})(?:$|/.*))",
                    _VueIndexHandler,
                    d,
                ),
            ]

        def _tcp_port():
            return (
                PKDict(tcp_port=pkconfig.parse_positive_int(tcp_port))
                if tcp_port
                else PKDict()
            )

        c = config.cfg().ui_api.copy()
        server.start(
            attr_classes=quest.attr_classes(),
            api_classes=ui_api.api_classes(),
            http_config=c.pkupdate(
                PKDict(
                    uri_map=_prod_uri_map(c) if prod else _dev_uri_map(c),
                    **_tcp_port(),
                )
            ),
        )


class _ProxyHandler(tornado.web.RequestHandler):
    def initialize(self, proxy_url, **kwargs):
        super().initialize(**kwargs)
        self.http_client = tornado.httpclient.AsyncHTTPClient()
        self.proxy_url = proxy_url

    async def get(self):
        r = await self.http_client.fetch(f"{self.proxy_url}{self.request.uri}")
        self.set_status(r.code)
        self.set_header("Content-Type", r.headers["Content-Type"])
        self.write(r.body)


class _VueIndexHandler(tornado.web.StaticFileHandler):
    def get_absolute_path(self, root, path, *args, **kwargs):
        return super().get_absolute_path(root, self.default_filename)
