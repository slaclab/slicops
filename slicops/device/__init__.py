"""Basic device operations

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import epics
import slicops.device_db
import threading

# TODO(robnagler) configure via device_db
_TIMEOUT = 5


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

    def __init__(self, device_name):
        self.device_name = device_name
        self.meta = slicops.device_db.meta_for_device(device_name)
        self._destroyed = False
        self._accessor = PKDict()
        self.connected = False

    def accessor(self, accessor_name):
        """Get `_Accessor` for more complex operations

        Args:
            accessor_name (str): friendly name for PV for this device
        Returns:
            _Accessor: object holding PV state
        """
        if self._destroyed:
            raise AssertionError(f"destroyed {self}")
        return self._accessor.pksetdefault(
            accessor_name, lambda: _Accessor(self, accessor_name)
        )[accessor_name]

    def destroy(self):
        """Disconnect from PV's and remove state about device"""
        if self._destroyed:
            return
        self._destroyed = True
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

    def __repr__(self):
        return f"<Device {self.device_name}>"


class _Accessor:
    """Container for a PV, metadata, and dynamic state

    Attributes:
        device (Device): object holding this accessor
        meta (PKDict): meta data about the accessor, e.g. pv_name, pv_writable
    """

    def __init__(self, device, accessor_name):
        self.device = device
        self.accessor_name = accessor_name
        self.meta = device.meta.accessor[accessor_name]
        self._callback = None
        self._destroyed = False
        self._lock = threading.Lock()
        self._initialized = threading.Event()
        self._initializing = False
        # Defer initialization
        self._pv = None

    def destroy(self):
        """Stop all monitoring and disconnect from PV"""
        if self._destroyed:
            return
        with self._lock:
            if self._destroyed:
                return
            self._destroyed = True
            self._initializing = False
            self._callback = None
            if (p := self._pv) is None:
                return
            self._pv = None
            self._initialized.set()
        try:
            # Clears all callbacks
            p.disconnect()
        except Exception as e:
            pkdlog("error={} {} stack={}", e, self, pkdexc())

    def get(self):
        """Read from PV

        Returns:
            object: the value from the PV converted to a Python type
        """
        p = self.__pv()
        if (rv := p.get(timeout=_TIMEOUT)) is None:
            raise DeviceError(f"unable to get {self}")
        if not p.connected:
            raise DeviceError(f"disconnected {self}")
        return self._fixup_value(rv)

    def monitor(self, callback):
        """Monitor PV and call callback with updates and connection changes

        The argument to the callback is a `PKDict` with one or more of:
            error : str
                error occured in the values from the PV callback (unlikely)
            value : object
                PV reported this change
            connected : bool
                connection state changed: True if connected

        Args:
            callback (callable): accepts a single `PKDict` as ag
        """
        with self._lock:
            self._assert_not_destroyed()
            if self._callback:
                raise AssertionError("may only call monitor once")
            if self._pv or self._initializing:
                raise AssertionError("monitor must be called before get/put")
            self._callback = callback
        self.__pv()

    def monitor_stop(self):
        """Stops monitoring PV"""
        with self._lock:
            if self._destroyed or not self._callback:
                return
            self._callback = None

    def put(self, value):
        """Set PV to value

        Args:
            value (object): Value to write to PV
        """
        if not self.meta.pv_writable:
            raise AccessorPutError(f"read-only {self}")
        if self.meta.py_type == bool:
            v = bool(value)
        elif self.meta.py_type == int:
            v = int(value)
        elif self.meta.py_type == float:
            v = float(value)
        else:
            raise AccessorPutError(f"unhandled py_type={self.meta.py_type} {self}")
        # ECA_NORMAL == 0 and None is normal, too, apparently
        p = self.__pv()
        if (e := p.put(v)) != 1:
            raise DeviceError(f"put error={e} value={v} {self}")
        if not p.connected:
            raise DeviceError(f"disconnected {self}")

    def _assert_not_destroyed(self):
        if self._destroyed:
            raise AssertionError(f"destroyed {self}")

    def _fixup_value(self, raw):
        def _reshape(image):
            return image.reshape(self._image_shape)

        if self.meta.py_type == bool:
            return bool(raw)
        if self.accessor_name == "image":
            return _reshape(raw)
        return raw

    def _on_connection(self, **kwargs):
        try:
            if "conn" not in kwargs:
                # This shouldn't happen
                pkdlog("missing 'conn' in kwargs={}", kwargs)
                self._run_callback(error="missing conn")
            else:
                self._run_callback(connected=kwargs["conn"])
        except Exception as e:
            pkdlog("error={} {} stack={}", e, self, pkdexc())
            raise

    def _on_value(self, **kwargs):
        try:
            if (v := kwargs.get("value")) is None:
                pkdlog("missing 'value' in kwargs={} {}", kwargs, self)
                self._run_callback(error="missing value or None")
            else:
                if self.meta.accessor_name == "image" and not len(v):
                    pkdlog("empty image received {}", self)
                    return
                self._run_callback(value=self._fixup_value(v))
        except Exception as e:
            pkdlog("error={} {} stack={}", e, self, pkdexc())
            raise

    def __pv(self):
        with self._lock:
            self._assert_not_destroyed()
            if self._pv:
                return self._pv
            if not (i := self._initializing):
                self._initializing = True
        if i:
            self._initialized.wait(timeout=_TIMEOUT)
        else:
            k = (
                PKDict(callback=self._on_value, auto_monitor=True)
                if self._callback
                else PKDict()
            )
            if self.accessor_name == "image":
                # TODO(robnagler) this has to be done here, because you can't get pvs
                # from within a monitor callback.
                # TODO(robnagler) need a better way of dealing with this
                self._image_shape = (self.device.get("n_row"), self.device.get("n_col"))
            self._pv = epics.PV(
                self.meta.pv_name,
                connection_callback=self._on_connection,
                connection_timeout=_TIMEOUT,
                **k,
            )
            self._initialized.set()
        return self._pv

    def __repr__(self):
        return f"<_Accessor {self.device.device_name}.{self.accessor_name} {self.meta.pv_name}>"

    def _run_callback(self, **kwargs):
        k = PKDict(accessor=self, **kwargs)
        with self._lock:
            c = self._callback
        if c:
            c(k)
