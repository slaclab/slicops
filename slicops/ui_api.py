"""UI API server implementation

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.quest


class UIAPI(slicops.quest.API):
    """API entry points to be dispatched

    All entry points take ``api_args``, which is a dictionary of arguments.

    Entry points return a `PKDict`, but could be an any Python data structure.

    Or, raise a `pykern.quest.APIError`.
    """

    async def api_echo(self, api_args):
        return api_args
