"""Device operations

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import epics
import slicops.device_db


class AccessorPutError(RuntimeError):
    """The PV for this accessor is not writable"""

    pass


class DeviceError(RuntimeError):
    """Error communicating with device"""

    pass


class Device:
    """Wrapper around physical device

    Attributes:
      name (str): name of device
      meta (slicops.device_db.DeviceMeta): information about device
    """

    def __init__(self, name):
        self.name = name
        self.meta = slicops.device_db.meta_for_device(name)
        self._pv = PKDict()

    def destroy(self):
        """Disconnect from PV's and remove state about device"""
        for n, p in self._pv.items():
            try:
                p.disconnect()
            except Exception as e:
                pkdlog("disconnect error={} pv={} stack={}", e, p.pvname, pkdexc())
        self._pv = PKDict()

    def get(self, accessor):
        """Read from PV

        Args:
          accessor (str): Friendly name for PV
        Returns:
          Any: the value from the PV converted to a Python friendly type
        """

        def _reshape(image):
            # TODO(robnagler) does get return 0 ever?
            if not ((r := self.get("num_rows")) and (c := self.get("num_cols"))):
                raise ValueError("num_rows or num_cols is invalid")
            return image.reshape(c, r)

        a, p = self._accessor_pv(accessor)
        if (rv := p.get()) is None or not p.connected:
            raise DeviceError(
                f"unable to get accessor={accessor} device={self.name} pv={a.pv_name}"
            )
        if a.py_type == "bool":
            return bool(rv)
        if a.name == "image":
            return _reshape(rv)
        return rv

    def has_accessor(self, accessor):
        """Check whether device has accessor

        Args:
          accessor (str): Friendly name for PV
        Returns:
          bool: True if PV is bound to device
        """
        return accessor in self.meta.accessor

    def put(self, accessor, value):
        """Set PV to value

        Args:
          accessor (str): Friendly name for PV
          value (Any): Value to write to PV
        """
        a, p = self._accessor_pv(accessor, write=True)
        # ECA_NORMAL == 0 and None is normal, too, apparently
        if (e := p.put(value)) != 1:
            if not p.connected:
                raise DeviceError(f"device={self.name} not connected pv={a.pv_name}")
            raise DeviceError(
                f"put error={e} accessor={accessor} value={value} to device={self.name} pv={a.pv_name}"
            )

    def _accessor_pv(self, accessor, write=False):
        a = self.meta.accessor[accessor]
        if write and not a.pv_writable:
            raise AccessorPutError(
                f"not writable accessor={accessor} to device={self.name} pv={a.pv_name}"
            )
        return (
            a,
            self._pv.pksetdefault(accessor, lambda: epics.PV(a.pv_name))[accessor],
        )
