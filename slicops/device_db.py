"""Accessing meta data about devices

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import numpy
import slicops.device_sql_db

_ACCESSOR_META = PKDict(
    acquire=PKDict(py_type=bool, pv_writable=True),
    image=PKDict(py_type=numpy.ndarray, pv_writable=False),
    n_bits=PKDict(py_type=int, pv_writable=False),
    n_col=PKDict(py_type=int, pv_writable=False),
    n_row=PKDict(py_type=int, pv_writable=False),
)


_WIRE_META = PKDict(
    HTR=PKDict(
        lblms=("LBLM01A:HTR", "LBLM01B:HTR"),
        bpms_before_wire=("BPMS:GUNB:925", "BPMS:HTR:120", "BPMS:HTR:320"),
        bpms_after_wire=(
            "BPMS:HTR:760",
            "BPMS:HTR:830",
            "BPMS:HTR:860",
            "BPMS:HTR:960",
        ),
    ),
    DIAG0=PKDict(
        lblms=("SBLM01A:DIAG0"),
        bpms_before_wire=(
            "BPMS:DIAG0:190",
            "BPMS:DIAG0:210",
            "BPMS:DIAG0:230",
            "BPMS:DIAG0:270",
            "BPMS:DIAG0:285",
            "BPMS:DIAG0:330",
            "BPMS:DIAG0:370",
            "BPMS:DIAG0:390",
        ),
        bpms_after_wire=("BPMS:DIAG0:470", "BPMS:DIAG0:520"),
    ),
    COL1=PKDict(
        lblms=("LBLM03A:L1B", "LBLM04A:L2B", "TMITLOSS:COL1"),
        bpms_before_wire=(
            "BPMS:BC1B:125",
            "BPMS:BC1B:440",
            "BPMS:COL1:120",
            "BPMS:COL1:260",
            "BPMS:COL1:280",
            "BPMS:COL1:320",
        ),
        bpms_after_wire=(
            "BPMS:BPN27:400",
            "BPMS:BPN28:200",
            "BPMS:BPN28:400",
            "BPMS:SPD:135",
            "BPMS:SPD:255",
            "BPMS:SPD:340",
            "BPMS:SPD:420",
            "BPMS:SPD:525",
        ),
    ),
    EMIT2=PKDict(
        lblms=("LBLM04A:L2B", "LBLM07A:L3B", "TMITLOSS:EMIT2"),
        bpms_before_wire=(
            "BPMS:BC2B:150",
            "BPMS:BC2B:530",
            "BPMS:EMIT2:150",
            "BPMS:EMIT2:300",
        ),
        bpms_after_wire=(
            "BPMS:SPS:780",
            "BPMS:SPS:830",
            "BPMS:SPS:840",
            "BPMS:SLTS:150",
            "BPMS:SLTS:430",
            "BPMS:SLTS:460",
        ),
    ),
    BYP=PKDict(
        lblms=("LBLM11A_1:BYP", "LBLM11A_2:BYP", "LBLM11A_3:BYP", "TMITLOSS:BYP"),
        bpms_before_wire=(
            "BPMS:L3B:3583",
            "BPMS:EXT:351",
            "BPMS:EXT:748",
            "BPMS:DOG:120",
            "BPMS:DOG:135",
            "BPMS:DOG:150",
            "BPMS:DOG:200",
            "BPMS:DOG:215",
            "BPMS:DOG:230",
            "BPMS:DOG:280",
            "BPMS:DOG:335",
            "BPMS:DOG:355",
            "BPMS:DOG:405",
        ),
        bpms_after_wire=(
            "BPMS:BPN23:400",
            "BPMS:BPN24:400",
            "BPMS:BPN25:400",
            "BPMS:BPN26:400",
            "BPMS:BPN27:400",
            "BPMS:BPN28:200",
            "BPMS:BPN28:400",
            "BPMS:SPD:135",
            "BPMS:SPD:255",
            "BPMS:SPD:340",
            "BPMS:SPD:420",
            "BPMS:SPD:525",
            "BPMS:SPD:570",
            "BPMS:SPD:700",
            "BPMS:SPD:955",
        ),
    ),
    SPD=PKDict(
        lblms=("LBLM22A:SPS"),
        bpms_before_wire=(
            "BPMS:SPD:135",
            "BPMS:SPD:255",
            "BPMS:SPD:340",
            "BPMS:SPD:420",
            "BPMS:SPD:525",
            "BPMS:SPD:570",
        ),
        bpms_after_wire=("BPMS:SPD:700", "BPMS:SPD:955", "BPMS:SLTD:625"),
    ),
    LTUS=PKDict(
        lblms=(
            "LBLMS32A:LTUS",
            "TMITLOSS:LTUS",
        ),
        bpms_before_wire=(
            "BPMS:BPN27:400",
            "BPMS:BPN28:200",
            "BPMS:BPN28:400",
            "BPMS:SPD:135",
            "BPMS:SPD:255",
            "BPMS:SPD:340",
            "BPMS:SPS:572",
            "BPMS:SPS:580",
            "BPMS:SPS:640",
            "BPMS:SPS:710",
            "BPMS:SPS:770",
            "BPMS:SPS:780",
            "BPMS:SPS:830",
            "BPMS:SPS:840",
            "BPMS:SLTS:150",
        ),
        bpms_after_wire=("BPMS:DMPS:381", "BPMS:DMPS:502", "BPMS:DMPS:693"),
    ),
)


class DeviceMeta(PKDict):
    """Information about a device

    Attributes:
        accessor (PKDict): name to PKDict(name, pv_base, pv_name, pv_writable, py_type)
        area (str): area where device is located
        beam_path (tuple): which beam paths does it go through
        device_kind (str): kind of device, e.g. "screen"
        device_type (str): type device, e.g. "PROF"
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
