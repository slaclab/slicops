"""Fractals app

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import numpy as np
import slicops.sliclet.yaml_db


class Fractals(slicops.sliclet.yaml_db.YAMLDb):

    def on_change_mode(self, txn, value, **kwargs):
        j = value == "Julia"
        txn.multi_set(
            ("density_i.ui.visible", j),
            ("density_r.ui.visible", j),
        )


CLASS = Fractals
