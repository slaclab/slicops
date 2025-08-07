"""Control a Screen

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
from slicops.device import DeviceError
import abc
import enum
import logging
import pykern.pkconfig
import queue
import slicops.device
import slicops.device_db
import threading

# TODO(robnagler) these should be reused for both cases
_MOVE_TARGET_IN = PKDict({False: 0, True: 1})
_STATUS_IN = 2
_STATUS_OUT = 1

_BLOCKING_MSG = "upstream target is in"
_TIMEOUT_MSG = "upstream target status accessor timed out"
_ERROR_PREFIX_MSG = "upstream target error: "


class DeviceScreen(slicops.device.Device):
    """Augment Device with screen specific operations"""

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

    def move_target(self, want_in):
        self.__worker.req_action(
            self.__worker.action_req_move_target, PKDict(want_in=want_in)
        )


class ErrorKind(enum.Enum):
    fsm = enum.auto()
    monitor = enum.auto()
    upstream = enum.auto()


class EventHandler:

    @abc.abstractmethod
    def on_screen_device_error(self, accessor_name, error_kind, error_msg):
        pass

    @abc.abstractmethod
    def on_screen_device_update(self, accessor_name, value):
        pass


class _FSM:
    def __init__(self, worker, handler):
        self.worker = worker
        self.handler = handler
        self.curr = PKDict(
            acquire=False,
            check_upstream=False,
            move_target_arg=None,
            target_status=None,
            upstream_problems=None,
        )
        self.prev = self.curr.copy()

    def event(self, name, arg):
        self.prev = self.curr.copy()
        pkdp((name, arg))
        if u := getattr(self, f"_event_{name}")(arg, **self.curr):
            self.curr.update(u)
        pkdp(u)

    def _event_handle_monitor(self, arg, **kwargs):
        n = arg.accessor.accessor_name
        if "error" in arg:
            self.handler.on_screen_device_error(
                error_kind=ErrorKind.monitor, accessor_name=n, error_msg=arg.error
            )
            if n == "target_status":
                # TODO(robnagler) is resetting move_target_arg right?
                return PKDict(target_status=None, move_target_arg=None)
            return
        if "connected" in arg:
            return
        if n == "image":
            v = arg.value
            rv = None
        elif n == "acquire":
            v = arg.value
            rv = PKDict(acquire=arg.value)
        elif n == "target_status":
            v = _STATUS_IN == arg.value
            rv = PKDict(move_target_arg=None, target_status=v)
        else:
            raise AssertionError(f"unsupported accessor={n} {self}")
        self.handler.on_screen_device_update(accessor_name=n, value=v)
        return rv

    def _event_move_target(
        self,
        arg,
        check_upstream,
        move_target_arg,
        target_status,
        upstream_problems,
        **kwargs,
    ):
        if move_target_arg:
            self.handler.on_screen_device_error(
                error_kind="fsm", error_msg="target already moving"
            )
            return
        if target_status is not None and arg.want_in == target_status:
            # TODO(robnagler) could be a race condition so probably fine to do nothing
            pkdlog("same target_status={} self.want_in={}", target_status, arg.want_in)
            return
        # TODO(robnagler) allow moving without checking upstream
        rv = PKDict(move_target_arg=arg)
        if arg.want_in and upstream_problems is None or upstream_problems:
            # Recheck the upstream
            self.worker.action(self.worker.action_check_upstream, None)
            rv.check_upstream = True
        return rv

    def _event_upstream_status(self, arg, move_target_arg, **kwargs):
        rv = PKDict(check_upstream=False, upstream_problems=arg.problems)
        if arg.problems:
            self.handler.on_screen_device_error(
                error_kind="upstream", error_msg=arg.problems
            )
            return rv.pkupdate(move_target_arg=None)
        self.worker.action(self.worker.action_move_target, move_target_arg)
        return rv

    def __repr__(self):
        def _states(curr):
            return " ".join(f"{k}={curr[k]}" for k in sorted(curr.keys()))

        return f"<_FSM {self.worker.device.device_name} {_states(self.curr)}>"


class _Thread:
    _LOOP_END = object()

    def __init__(self):
        self.destroyed = False
        self.__lock = threading.Lock()
        self.__actions = queue.Queue()
        self.__thread = threading.Thread(target=self._loop, daemon=True)
        if self._loop_timeout_secs > 0 and not hasattr(self, "action_loop_timeout"):
            raise AssertionError(
                f"_loop_timeout_secs={self._loop_timeout_secs} and not action_loop_timeout"
            )
        self.__thread.start()

    def action(self, method, arg):
        self.__actions.put_nowait((method, arg))

    def destroy(self):
        try:
            with self.__lock:
                if self.destroyed:
                    return
                self.destroyed = True
                self.__actions.put_nowait((None, None))
                self._destroy()
        except Exception as e:
            pkdlog("error={} {} stack={}", e, self, pkdexc(simplify=True))

    def _loop(self):
        timeout_kwarg = PKDict()
        if self._loop_timeout_secs:
            timeout_kwarg.timeout = self._loop_timeout_secs
        try:
            while True:
                try:
                    m, a = self.__actions.get(**timeout_kwarg)
                except queue.Empty:
                    m, a = self.action_loop_timeout(), None
                with self.__lock:
                    if self.destroyed:
                        return
                    if m(a) is self._LOOP_END:
                        return
        except Exception as e:
            pkdlog("error={} {} stack={}", e, self, pkdexc(simplify=True))
        finally:
            self.destroy()

    def __repr__(self):
        def _destroyed():
            return " DESTROYED" if self.destroyed else ""

        return f"<{self.__class__.__name__}{_destroyed()} self._repr()>"


class _Upstream(_Thread):
    def __init__(self, worker):
        def _names():
            return slicops.device_db.upstream_devices(
                "PROF", "target_control", worker.beam_path, worker.device.device_name
            )

        self.__worker = worker
        self.__problems = PKDict()
        self.__devices = PKDict({u: slicops.device.Device(u) for u in _names()})
        self._loop_timeout_secs = _cfg.upstream_timeout_secs
        super().__init__()

    def action_handle_status(self, arg):
        n = arg.accessor.device.device_name
        self.__devices.pkdel(n).destroy()
        if e := arg.get("error"):
            pkdlog("device={} error={}", n, e)
            self.__problems[n] = f"{_ERROR_PREFIX_MSG}{e}"
        elif arg.value == _STATUS_IN:
            self.__problems[n] = _BLOCKING_MSG
        if not self.__devices:
            return self.__done()
        return None

    def action_loop_timeout(self):
        for n in self.__devices:
            self.__problems[n] = _TIMEOUT_MSG
        return self.__done()

    def _destroy(self):
        (d, self.__devices) = (self.__devices, PKDict())
        for x in d.values():
            x.destroy()

    def __done(self):
        self.__worker.action(
            self.__worker.action_upstream_status, PKDict(problems=self.__problems)
        )
        return self._LOOP_END

    def __handle_status(self, kwargs):
        if "connected" in kwargs:
            return
        self.action(self.action_handle_status, kwargs)

    def _loop(self, *args, **kwargs):
        for d in self.__devices.values():
            d.accessor("target_status").monitor(self.__handle_status)
        super()._loop(*args, **kwargs)

    def _repr(self):
        return f"pending={sorted(self.__devices)} problems={sorted(self.__problems)}"


class _Worker(_Thread):
    """Implements actions of DeviceScreen"""

    def __init__(self, beam_path, handler, device):
        self.beam_path = beam_path
        self.device = device
        self.__upstream = None
        self.__status = None
        self.__fsm = _FSM(self, handler)
        self.__target_control = None
        self._loop_timeout_secs = 0
        super().__init__()

    def action_check_upstream(self, arg):
        self.__upstream = _Upstream(self)
        return None

    def action_handle_monitor(self, arg):
        self.__fsm.event("handle_monitor", arg)
        return None

    def action_move_target(self, arg):
        pkdp(arg)
        if not self.__target_control:
            self.__target_control = self.device.accessor("target_control")
        self.__target_control.put(pkdp(_MOVE_TARGET_IN[arg.want_in]))
        return None

    def action_req_move_target(self, arg):
        pkdp(arg)
        self.__fsm.event("move_target", arg)
        return None

    def action_upstream_status(self, arg):
        self.__fsm.event("upstream_status", arg)
        self.__upstream = None
        return None

    def req_action(self, method, arg):
        """Called by DeviceScreen which has separate life cycle"""
        if self.destroyed:
            raise AssertionError("object is destroyed")
        self.action(method, arg)

    def _destroy(self):
        if self.__upstream:
            (u, self.__upstream) = (self.__upstream, None)
            u.destroy()

    def __handle_monitor(self, change):
        self.action(self.action_handle_monitor, change)

    def _loop(self, *args, **kwargs):
        for a in "acquire", "image", "target_status":
            self.device.accessor(a).monitor(self.__handle_monitor)
        super()._loop(*args, **kwargs)

    def _repr(self):
        return f"device={self.device.device_name}"


_cfg = pykern.pkconfig.init(
    upstream_timeout_secs=(
        15,
        pykern.pkconfig.parse_seconds,
        "how long to wait for updates from devices",
    ),
)
