"""Device operations

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import epics
import slicops.device_db
import threading


class AccessorPutError(RuntimeError):
    """The PV for this accessor is not writable"""

    pass


class DeviceError(RuntimeError):
    """Error communicating with PV"""

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
        self._accessor = PKDict()
        self.connected = False

    def accessor(self, accessor_name):
        """Get `_Accessor` for more complex operations

        Args:
            accessor_name (str): friendly name for PV for this device
        Returns:
            _Accessor: object holding PV state
        """
        return self._accessor.pksetdefault(
            accessor_name, lambda: _Accessor(self, accessor_name)
        )[accessor_name]

    def destroy(self):
        """Disconnect from PV's and remove state about device"""
        x = list(self._accessor.values())
        self._accessor = PKDict()
        for a in x:
            a.destroy()

    def get(self, accessor_name):
        """Read from PV

        Args:
            accessor_name (str): friendly name for PV for this device
        Returns:
            object: the value from the PV converted to a Python type
        """
        return self.accessor(accessor_name).get()

    def has_accessor(self, accessor_name):
        """Check whether device has accessor

        Args:
            accessor_name (str): friendly name for PV for this device
        Returns:
            bool: True if accessor is found for device
        """
        return accessor_name in self.meta.accessor

    def put(self, accessor_name, value):
        """Set PV to value

        Args:
            accessor_name (str): friendly name for PV for this device
            value (object): Value to write to PV
        """
        return self.accessor(accessor_name).put(value)


class _Accessor:

    def __init__(self, device, name):
        self.meta = self.device.meta.accessor[name]
        self.device = device
        self.pv = epics.PV(self.meta.pv_name, connection_callback=self._on_connection)
        self._callback = None
        self._mutex = threading.Lock()
        self._destroyed = False

    def disconnect():
        """Stop all monitoring and disconnect from PV"""
        self._callback = None
        try:
            # Clears all callbacks
            self.pv.disconnect()
        except Exception as e:
            pkdlog("error={} {} stack={}", e, self, pkdexc())

    def get(self, accessor_name):
        """Read from PV

        Returns:
            object: the value from the PV converted to a Python type
        """

        if (rv := self.pv.get()) is None:
            raise DeviceError(f"unable to get {self}")
        if not self.pv.connected:
            raise DeviceError(f"disconnected {self}")
        return self._fixup_value(rv)

    def monitor(self, callback):
        with self._mutex:
            if self._callback:
                raise ValueError(f"already monitoring {self}")
            # should lock
            self._callback_index = self.pv.add_callback(self._on_value)
            a.pv.auto_monitor = True
            self._callback = callback

    def monitor_stop(self):
        with self._mutex:
            if not self._callback:
                return
            self._callback = None
            self.pv.auto_monitor = False
            self.pv.remove_callback(self._callback_index)
            self._callback_index = None

    def put(self, value):
        """Set PV to value

        Args:
            value (object): Value to write to PV
        """
        if not self.meta.pv_writable:
            raise AccessorPutError(f"read-only {self}")
        # ECA_NORMAL == 0 and None is normal, too, apparently
        if (e := self.pv.put(value)) != 1:
            raise DeviceError(f"put error={e} value={value} {self}")
        if not self.pv.connected:
            raise DeviceError(f"disconnected {self}")

    def _fixup_value(self, raw, accessor_meta):
        def _reshape(image):
            # TODO(robnagler) does get return 0 ever?
            if not ((r := self.get("num_rows")) and (c := self.get("num_cols"))):
                raise ValueError("num_rows or num_cols is invalid")
            return image.reshape(c, r)

        if accessor_meta.py_type == "bool":
            return bool(raw)
        if accessor_meta.name == "image":
            return _reshape(raw)
        return raw

    def _on_connection(self, **kwargs):
        if "conn" not in kwargs:
            # This shouldn't happen
            pkdlog("missing 'conn' in kwargs={}", kwargs)
            self._run_callback(error="missing conn")
        else:
            self._run_callback(conn=conn)

    def _on_value(self, **kwargs):
        if (v := kwargs.get("value")) is None:
            pkdlog("missing 'value' in kwargs={} {}", kwargs, self)
            self._run_callback(error="missing value or None")
        else:
            self._run_callback(value=self._fixup_value(v))

    def __repr__(self):
        return f"_Accessor({self.device.name}.{self.name}, {self.meta.pv_name})"

    def _run_callback(self, **kwargs):
        k = PKDict(accessor=self, **kwargs)
        with self._mutex:
            c = self._callback
        if c:
            c(k)
