"""Device operations

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import epics
import slicops.device_meta_raw


class DeviceError(RuntimeError):
    pass


class Device:

    def __init__(self, name):
        if not (m := slicops.device_meta_raw.DB.DEVICE_TO_META.get(name)):
            raise NameError(f"no such device={name}")
        # TODO(robnagler) support types based on rules
        if m.device_kind != "screen":
            raise NotImplementedError(
                f"unsupported device_kind={m.device_kind} device={name}"
            )
        self.name = name
        self._meta = m
        self._pv = PKDict()

    def get(self, accessor):
        a, p = self._accessor_pv(accessor)
        if (rv := p.get()) is None or not p.connected:
            raise DeviceError(
                f"unable to get accessor={accessor} device={self.name} pv={a.pv_name}"
            )
        if a.py_type == "bool":
            return bool(rv)
        return rv

    def put(self, accessor, value):
        a, p = self._accessor_pv(accessor)
        # ECA_NORMAL == 0 and None is normal, too, apparently
        if (e := p.put(value)) != 1:
            if not p.connected:
                raise DeviceError(f"device={self.name} not connected pv={a.pv_name}")
            raise DeviceError(
                f"put error={e} accessor={accessor} value={value} to device={self.name} pv={a.pv_name}"
            )

    def _accessor_pv(self, accessor):
        a = self._meta.accessor[accessor]
        return (
            a,
            self._pv.pksetdefault(accessor, lambda: epics.PV(a.pv_name))[
                accessor
            ],
        )
