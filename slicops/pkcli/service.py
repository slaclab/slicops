"""Start SlicOps services.

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.pkcli


class Commands(slicops.pkcli.CommandsBase):

    def ui_api(self):
        """Start UI API web server.

        This web server provides a friendly and secure API for the

        """
        from pykern.api import server
        from slicops import config, ui_api, quest

        server.start(
            attr_classes=quest.attr_classes(),
            api_classes=ui_api.api_classes(),
            http_config=config.cfg().ui_api.copy(),
        )
