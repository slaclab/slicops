"""SlicOps EPICS utilities.

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import epics


def init_dev():
    """Initialize the ADSimDetector module with useful default values."""
    for name, value in {
        "13SIM1:cam1:SimMode": 1,
        "13SIM1:cam1:PeakStartX": 600,
        "13SIM1:cam1:PeakStartY": 400,
        "13SIM1:cam1:PeakNumX": 1,
        "13SIM1:cam1:PeakNumY": 2,
        "13SIM1:cam1:PeakStepX": 300,
        "13SIM1:cam1:PeakStepY": 140,
        "13SIM1:cam1:PeakWidthX": 90,
        "13SIM1:cam1:PeakWidthY": 60,
        "13SIM1:cam1:PeakVariation": 10,
        "13SIM1:cam1:Noise": 50,
        "13SIM1:cam1:Gain": 100,
        "13SIM1:cam1:AcquirePeriod": 0.5,
        "13SIM1:cam1:SizeX": 1024,
        "13SIM1:cam1:SizeY": 768,
        "13SIM1:image1:EnableCallbacks": 1,
    }.items():
        pv = epics.PV(name)
        v = pv.put(value, wait=True)
        if not pv.connected:
            raise RuntimeError(f"PV failed to connect: {name}")
        if not v:
            raise RuntimeError(f"PV put failed to return a succes value: {name}")
