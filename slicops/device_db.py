"""Accessing meta data about devices

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.device_db_sql


class DeviceMeta(PKDict):
    """Information about a device

    Attributes:
        accessor (PKDict): name to PKDict(name, pv_base, pv_name, pv_writable, py_type)
        area (str): area where device is located
        beam_path (tuple): which beam paths does it go through
        device_kind (str): kind of device, e.g. "screen"
        device_length (float): length in meters
        device_name (str): name of device
        pv_prefix (str): prefix to all accessor PVs for device
    """

    def __init__(self, values):
        super().__init__(values)


def beam_paths():
    """Get all beam path names

    Returns:
        tuple: sorted beams path names
    """
    return tuple(slicops.device_meta_raw.DB.BEAM_PATH_TO_DEVICE.keys())


def devices_for_beam_path(beam_path, device_kind):
    """Look up all device_kind in beam_path

    Args:
        beam_path (str): which beam path
        device_kind (str): kind of device to filter by
    Returns:
        tuple: sorted device names
    """
    if device_kind not in slicops.device_meta_raw.DB.DEVICE_KIND_TO_DEVICE:
        raise NameError(f"no such device_kind={device_kind}")
    return tuple(
        n
        for n in slicops.device_meta_raw.DB.BEAM_PATH_TO_DEVICE[beam_path]
        if slicops.device_meta_raw.DB.DEVICE_TO_META[n].device_kind == device_kind
    )


def meta_for_device(device_name):
    """Look up meta data for device_name

    Args:
        device_name (str): which device
    Returns:
        DeviceMeta: information about device
    """
    return DeviceMeta(slicops.device_meta_raw.DB.DEVICE_TO_META[device_name])
