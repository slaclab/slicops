"""Accessing meta data about devices

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import numpy
import slicops.const
import slicops.device_sql_db


class DeviceDbError(Exception):
    pass


class DeviceMeta(PKDict):
    """Information about a device

    Attributes:
        accessor (PKDict): name to PKDict(name, cs_name, writable, py_type, ...)
        beam_area (str): area where device is located
        beam_path (tuple): which beam paths does it go through
        device_type (str): type device, e.g. "PROF"
        device_name (str): name of device
        cs_name (str): prefix to all accessors for device
    """

    pass


def beam_paths():
    """Get all beam path names

    Returns:
        tuple: sorted beams path names
    """
    rv = slicops.device_sql_db.beam_paths()
    # TODO(robnagler) probably don't need this check
    if not rv:
        raise DeviceDbError("no beam_paths")
    return rv


def device_names(device_type, beam_path):
    """Query devices for device_type and beam_path

    Args:
        device_type (str): type of device to filter by
        beam_path (str): which beam path
    Returns:
        tuple: sorted device names
    """
    if rv := slicops.device_sql_db.device_names(
        _assert_device_type(device_type), beam_path
    ):
        return rv
    # TODO(robnagler) refine because beam_path could exist, just not for device
    raise DeviceDbError(f"no devices for beam_path={beam_path}")


def meta_for_device(device_name):
    """Look up meta data for device_name

    Args:
        device_name (str): which device
    Returns:
        DeviceMeta: information about device
    """

    rv = DeviceMeta(slicops.device_sql_db.device(device_name))
    # TODO(robnagler) probably don't need this check
    if not rv.accessor:
        raise DeviceDbError(
            f"no accessors for device_name={device_name} device_meta={rv}"
        )
    return rv


def upstream_devices(device_type, accessor_name, beam_path, device_name):
    """returns in z order"""
    return slicops.device_sql_db.upstream_devices(
        _assert_device_type(device_type),
        accessor_name,
        beam_path,
        device_name,
    )


def _assert_device_type(value):
    if value not in slicops.const.DEVICE_TYPES:
        raise DeviceDbError(f"no such device_type={value}")
    return value
