"""UI APIs

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.ui_api.screen
import slicops.ui_api.simple


def api_classes():
    return (slicops.ui_api.screen.API, slicops.ui_api.simple.API)
