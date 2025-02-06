"""Emulate epics.PV for unit tests

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import copy
import numpy
import sys
import threading
import time

MONITOR_X_SIZE = [50]  # , 100, 150, 200]

MONITOR_SLEEP = 0.1

_X_SIZE = 50
_Y_FACTOR = 1.3

_PV = None


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
        def _update():
            self.connection_callback(conn=True)
            for s in MONITOR_X_SIZE:
                time.sleep(MONITOR_SLEEP)
                _PV.pkupdate(_pv_image(s))
                self.monitor_callback(value=_PV[self.pvname])
            self.connection_callback(conn=False)

        self._auto_monitor = value
        if value:
            t = threading.Thread(target=_update)
            t.start()

    def get(self):
        # TOOD(robnagler) need to be more sophisticated

        return _PV.get(self.pvname, None)

    def put(self, value):
        _PV[self.pvname] = value
        return 1

    def remove_callback(self, index):
        if index != self._CB_INDEX:
            raise AssertionError(f"invalid index={index}")
        self.monitor_callback = None


def reset_state():
    global _PV

    _PV = PKDict(
        {
            "13SIM1:cam1:Gain": 93,
            "13SIM1:cam1:Acquire": 0,
            "13SIM1:cam1:N_OF_BITS": 8,
            "YAGS:IN20:211:N_OF_COL": 100,
            "YAGS:IN20:211:N_OF_ROW": 100,
        }
    ).pkupdate(_pv_image(_X_SIZE))


def _gaussian(x_size):
    sigma = x_size // 5

    def _dist(vec, is_y):
        s = _y_adjust(sigma) if is_y else sigma
        return (vec - vec.shape[0] // 2) ** 2 / (2 * (s**2))

    def _norm(mat):
        return ((mat - mat.min()) / (mat.max() - mat.min())) * 255

    def _vec(size):
        return numpy.linspace(0, size - 1, size)

    x, y = numpy.meshgrid(_vec(x_size), _vec(_y_adjust(x_size)))
    return _norm(numpy.exp(-(_dist(x, False) + _dist(y, True))))


def _pv_image(size):
    return {
        "13SIM1:cam1:SizeX": size,
        "13SIM1:cam1:SizeY": _y_adjust(size),
        # numpy is row major ("C" style)
        "13SIM1:image1:ArrayData": _gaussian(size).flatten(),
    }


def _y_adjust(value):
    return int(value * _Y_FACTOR)


if "epics" in sys.modules:
    raise AssertionError("epics already imported, 'import mock_epics' first")
sys.modules["epics"] = sys.modules[PV.__module__]
