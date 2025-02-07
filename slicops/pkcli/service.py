"""Start SlicOps services.

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.pkcli


class Commands(slicops.pkcli.CommandsBase):

    def ui_api(self, tcp_port=None, prod=False):
        """Start UI API web server.

        This web server provides a friendly and secure API for the

        Args:
            prod (bool): run in production mode (serve angular statically)

        """
        from pykern import pkconfig, pkresource
        from pykern.api import server
        from slicops import config, ui_api, quest
        from tornado import web

        def _ng_serve(config):
            if not prod:
                # TODO(robnagler) proxy ng serve
                return config
            config.uri_map = [
                (
                    # very specific so we control the name space
                    r"^(?:/screen/?|/)(\w+.\w+\.(?:css|js)|favicon.ico|)$",
                    web.StaticFileHandler,
                    PKDict(
                        path=str(pkresource.file_path("ng-build")),
                        default_filename="index.html",
                    ),
                ),
            ]
            return config

        def _port(config):
            if tcp_port is not None:
                config.tcp_port = pkconfig.parse_positive_int(tcp_port)
            return config

        server.start(
            attr_classes=quest.attr_classes(),
            api_classes=ui_api.api_classes(),
            http_config=_port(_ng_serve(config.cfg().ui_api.copy())),
        )
