"""Control a Screen

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp, pkdformat
import abc
import enum
import pykern.pkasyncio
import slicops.device

class Screen(slicops.device.Device):
    """Augment `Device` with screen specific operations"""

    def __init__(self, beam_path, device_name, handler, *args, **kwargs):
        super().__init__(device_name, *args, **kwargs)
        if not isinstance(handler, EventHandler):
            raise AssertionError(
                f"handler is not subclass EventHandler type={type(handler)}"
            )
        self.__worker = _Worker(beam_path, handler, self)

    def destroy(self):
        self.__worker.destroy()
        super().destroy()


class ErrorKind(enum.Enum):
    """Errors passed to on_screen_device_error"""

    monitor = enum.auto()


class EventHandler:
    """Clients of DeviceScreen must implement this"""

    @abc.abstractmethod
    def on_screen_device_error(self, exc):
        pass

    @abc.abstractmethod
    def on_screen_device_update(self, accessor_name, value):
        pass


class ScreenError(Exception):
    def __init__(self, **kwargs):
        def _arg_str():
            return pkdformat(
                " ".join(k + "={" + k + "}" for k in sorted(kwargs)),
                **kwargs,
            )

        super().__init__(_arg_str())


class _Worker(pykern.pkasyncio.ActionLoop):
    """Action loop for Screen

    Monitor calls from device are translated to actions to avoid locking in
    callback.
    """

    _MONITORS = ("acquire", "image")

    def __init__(self, beam_path, handler, device):
        self.beam_path = beam_path
        self.device = device
        self.__handler = handler
        self.__status = None
        self._loop_timeout_secs = 0
        super().__init__()

    def action_call_handler(self, arg):
        m = (
            self.__handler.on_screen_device_error
            if isinstance(arg, Exception)
            else self.__handler.on_screen_device_update
        )
        # Denormalized state so no need for lock during call
        if isinstance(arg, dict):
            return lambda: m(**arg)
        else:
            return lambda: m(arg)

    def action_handle_monitor(self, arg):
        n = arg.accessor.accessor_name
        if "error" in arg:
            self.action(
                "call_handler",
                ScreenError(
                    device=self.device.device_name,
                    error_kind=ErrorKind.monitor,
                    accessor_name=n,
                    error_msg=arg.error,
                ),
            )
            return
        if "connected" in arg:
            return
        if n not in self._MONITORS:
            raise AssertionError(f"unsupported accessor={n} {self}")
        self.action("call_handler", PKDict(accessor_name=n, value=arg.value))

    def req_action(self, method, arg):
        """Called by DeviceScreen which has separate life cycle"""
        if self.destroyed:
            raise AssertionError("object is destroyed")
        self.action(method, arg)

    def _destroy(self):
        pass

    def _handle_exception(self, exc):
        self.__handler.on_screen_device_error(
            ScreenError(
                device=self.device.device_name,
                error=exc,
            )
        )

    def __handle_monitor(self, change):
        self.action("handle_monitor", change)

    def _start(self, *args, **kwargs):
        for a in self._MONITORS:
            self.device.accessor(a).monitor(self.__handle_monitor)
        super()._start(*args, **kwargs)

    def _repr(self):
        return f"device={self.device.device_name}"
