"""Start SlicOps services.

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.pkcli


class Commands(slicops.pkcli.CommandsBase):

    def ui(self):
        """Start UI API web server.

        This web server provides a friendly and secure API for the

        """
        from pykern import http
        from slicops import config, ui_api, quest

        http.server_start(
            attr_classes=quest.attr_classes(),
            api_classes=(ui_api.UIAPI,),
            http_config=config.cfg().ui_api,
        )
