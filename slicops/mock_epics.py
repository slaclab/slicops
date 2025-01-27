"""mock epics.PV for slicops

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import numpy
import sys


# TODO(robnagler) to create an error, have a small radius
_RADIUS = 50


def _sphere(radius):

    def _scale(heatmap):
        return (
            (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min()) * 255
        ).astype(int)

    y, x = numpy.ogrid[-radius:radius, -radius:radius]
    # This has to be a variable otherwise doesn't compute right in where
    c = numpy.sqrt(x**2 + y**2)
    return _scale(numpy.sqrt(radius**2 - x**2 - y**2, where=c <= radius)).flatten()


_pv_values = PKDict(
    {
        "13SIM1:cam1:Gain": 93,
        "13SIM1:image1:ArrayData": _sphere(_RADIUS),
        "13SIM1:cam1:Acquire": 0,
        "13SIM1:cam1:ArraySizeX_RBV": _RADIUS * 2,
        "13SIM1:cam1:ArraySizeY_RBV": _RADIUS * 2,
        "13SIM1:cam1:N_OF_BITS": 8,
    }
)


class PV:
    def __init__(self, name):
        self.pvname = name
        self.connected = True

    def disconnect(self):
        pass

    def get(self):
        #TOOD(robnagler) need to be more sophisticated
        return _pv_values.get(self.pvname, None)

    def put(self, value):
        _pv_values[self.pvname] = value
        return 1


assert (
    "epics" not in sys.modules
), "epics already imported, this module must be imported first"
sys.modules["epics"] = sys.modules[PV.__module__]
