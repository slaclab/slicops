"""mock epics.PV for slicops

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import numpy
import sys
import threading

_SIZE = 50
_SIGMA = _SIZE // 5
_Y_FACTOR = 1.3

def _y_adjust(value):
    return int(value * _Y_FACTOR)

def _gaussian(size, sigma, y_factor):

    def _dist(vec, sigma_factor):
        return (vec - vec.shape[0] // 2) ** 2 / (2 * (_y_adjust(sigma) ** 2))

    def _vec(size):
        return numpy.linspace(0, size - 1, size)

    x, y = numpy.meshgrid(_vec(size), _vec(_y_adjust(size)))
    return numpy.exp(-(_dist(x, 1) + _dist(y, y_factor)))


_pv_values = PKDict(
    {
        "13SIM1:cam1:Gain": 93,
        "13SIM1:image1:ArrayData": _gaussian(_SIZE, _SIGMA, _Y_FACTOR),
        "13SIM1:cam1:Acquire": 0,
        "13SIM1:cam1:ArraySizeX_RBV": _SIZE,
        "13SIM1:cam1:ArraySizeY_RBV": _y_adjust(_SIZE),
        "13SIM1:cam1:N_OF_BITS": 8,
    }
)


class PV:
    _CB_INDEX = 1

    def __init__(self, name, connection_callback=None):
        self.pvname = name
        self.connected = True
        self.connection_callback = connection_callback
        self.monitor_callback = None
        self._auto_monitor = False

    def disconnect(self):
        pass

    def add_callback(self, callback):
        if self.monitor_callback:
            raise AssertionError("too many callbacks")
        self.monitor_callback = callback
        return self._CB_INDEX

    @property
    def auto_monitor(self):
        return self._auto_monitor

    @auto_monitor.setter
    def auto_monitor(self, value):
        self._auto_monitor = value

    def get(self):
        # TOOD(robnagler) need to be more sophisticated
        return _pv_values.get(self.pvname, None)

    def remove_callback(self, index):
        if index != self._CB_INDEX:
            raise AssertionError(f"invalid index={index}")
        self.monitor_callback = None

    def put(self, value):
        _pv_values[self.pvname] = value
        return 1


if "epics" in sys.modules:
    raise AssertionError("epics already imported, 'import mock_epics' first")
sys.modules["epics"] = sys.modules[PV.__module__]
