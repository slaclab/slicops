"""Base class and common routines for other pkcli's to inherit/use.

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp


class CommandsBase:
    """Common functionality between all pkclis"""

    def quest_start(self):
        """Begin a request which wraps all APIs."""
        from slicops import quest

        return quest.start()
