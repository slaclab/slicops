"""Device operations

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import epics
import slicops.device_meta_raw
import enum

class Device:

    def __init__(self, name):
        if not m := slicops.device_meta_raw.DEVICE_TO_META.get(name):
            raise NameError(f"no such device={name}")
        #TODO(robnagler) support types based on rules
        if m.device_kind != "screen":
            raise NotImplementedError(f"unsupported device_kind={m.device_kind} device={name}")
