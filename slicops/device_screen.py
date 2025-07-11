"""Accessing meta data about devices

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.device_db


def insert_prof_target(device_name):
    if _already_in(device_name):
        raise ValueError(f"device={device_name} already in")
    _assert_upstream_in(device_name)


def _already_in(device):

    pass

#    = slicops.device_db.upstream_devices(device_name)
