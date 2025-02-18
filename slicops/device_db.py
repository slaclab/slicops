"""Accessing meta data about devices

:copyright: Copyright (c) 2025 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.device_meta_raw
import copy


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
        super().__init__(copy.deepcopy(values))


# TODO(robnagler) are we selecting a machine?
def beam_paths():
    """Get all beam path names

    Returns:
        tuple: sorted beams path names
    """
    return tuple(sorted(slicops.device_meta_raw.DB.BEAM_PATH_TO_DEVICE.keys()))


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
    if (b := slicops.device_meta_raw.DB.BEAM_PATH_TO_DEVICE.get(beam_path)) is None:
        raise NameError(f"no such beam_path={beam_path}")
    return tuple(
        sorted(
            n
            for n in b
            if slicops.device_meta_raw.DB.DEVICE_TO_META[n].device_kind == device_kind
        )
    )


def meta_for_device(device_name):
    """Look up meta data for device_name

    Args:
        device_name (str): which device
    Returns:
        DeviceMeta: information about device
    """
    if not (rv := slicops.device_meta_raw.DB.DEVICE_TO_META.get(device_name)):
        raise NameError(f"no such device={device_name}")
    return DeviceMeta(rv)
