"""Control a Screen

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import logging
from slicops.device import DeviceError
import slicops.device
import slicops.device_db
import enum
import queue
import threading

# rjn these should be reused for both cases
_MOVE_TARGET_IN = PKDict(False=0, True=1)
_STATUS_IN = 2
_STATUS_OUT = 1

_BLOCKING_MSG = "upstream target is in"
_TIMEOUT_MSG = "upstream target status accessor timed out"
_ERROR_PREFIX_MSG = "upstream target error: "


class DeviceScreen(slicops.device.Device):
    """Augment Device with screen specific operations"""

    def __init__(self, beam_path, handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__worker = _Worker(beam_path, handler, self)

    def destroy(self):
        self.__worker.destroy()
        super().destroy()

    def move_target(self, want_in):
        self.__worker.req_action(self.action_req_move_target, PKDict(want_in=want_in))


class _FSM:
    def __init__(self, worker):
        self.worker = worker
        self.curr = PKDict(
            check_target=False,
            check_upstream=False,
            move_target=False,
            target_is_in=None,
            upstream_problems=None,
        )
        self.prev = self.curr.copy()

    def event(self, name, arg):
        self.prev = self.curr.copy()
        if u := getattr(self, f"_event_{name}")(arg, **self.curr):
            self.curr.update(u)

    def __repr__(self):
        def _states(curr):
            return " ".join(f"{k}={curr[k]}" for k in sorted(curr.keys()))

        return f"<_FSM {_states(self.curr)}>"
    def _event_move_target(self, arg, move_target, check_upstream, upstream_problems, **kwargs):
        if move_target:
            self.worker.handler.on_screen_fsm_error("target already moving")
            return
        #TODO(robnagler) allow moving without checking upstream
        rv = PKDict(move_target=True)
        if arg.want_in and upstream_problems is None or upstream_problems:
            self.worker.action(self.worker.action_check_upstream, None)
            rv.check_upstream = True
        return rv

    def _event_upstream_status_done(self, arg, check_upstream, **kwargs):
        if arg.problems:
            self.worker.handler.on_screen_upstream_problems(problems=arg.problems)
            return PKDict(check_upstream=False, move_target=None)
        self.worker.action(self.worker.action_move_target, None)
        return PKDict(check_upstream=False)


class _Thread:
    _LOOP_END = object()

    def __init__(self):
        self.destroyed = False
        self.__lock = threading.Lock()
        self.__actions = queue.Queue()
        self.__thread = threading.Thread(target=self._loop)
        if self._loop_timeout_secs > 0 and not hasattr(self, "action_loop_timeout"):
            raise AssertionError(f"_loop_timeout_secs={self._loop_timeout_secs} and not action_loop_timeout")
        self.__thread.start()

    def action(self, method, arg):
        self.__actions.put_nowait((method, arg))

    def destroy(self):
        try:
            with self.__lock:
                if self.destroyed:
                    return
                self.destroyed = True
                self.__actions.put_nowait(None, None)
                self._destroy()
        except Exception as e:
            pkdlog("error={} {} stack={}", e, self, pkdexc(simplify=True))

    def _destroy(self):
        pass

    def _loop(self):
        try:
            while True:
                try:
                    m, a = self.__actions.get(timeout=self._loop_timeout_secs)
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

        return f"<{self.__class__.__name}{_destroyed()} self._repr()>"


class _Upstream(_Thread):
    def __init__(self, worker, req_arg):
        def _names():
            return slicops.device_db.upstream_devices(
                "PROF", "target_control", parent.beam_path, parent.device_name
            )

        self.__worker = worker
        self.__callback_arg = req_arg
        self.__problems = PKDict()
        self.__devices = PKDict({u: slicops.device.Device(u) for u in _names()})
        self._loop_timeout_secs = _cfg.upstream_tim
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
        self.req_arg.problems = self.__problems
        self.__worker.action(self.__worker.action_upstream_status, self.__req_arg)
        return self._LOOP_END

    def __handle_status(self, **kwargs):
        self.action(self.action_handle_status, PKDict(kwargs))

    def _loop(self, *args, **kwargs):
        for d in self.__devices.values():
            d.accessor("target_status").monitor(self.__handle_status)
        super()._loop(*args, **kwargs)

    def _repr(self):
        return f"pending={sorted(self.__devices)} problems={sorted(self.__problems)}"


class _Worker(_Thread):
    """Implements actions of DeviceScreen"""

    def __init__(self, beam_path, handler, device):
        self.__beam_path = beam_path
        self.__handler = handler
        self.__device = device
        self.__upstream = None
        self.__status = None
        self.__fsm = __FSM(self)
        self._loop_timeout_secs = 0
        super().__init__()

    def action_monitor_acquire(self, arg):
        self.__handler.on_screen_acquire(is_acquiring=arg.value)
        self.__fsm.event("monitor_acquire", arg.value)
        return None

    def action_monitor_error(self, arg):
        self.__handler.on_screen_monitor_error(accessor=arg.accessor, error=arg.error)
        return None

    def action_monitor_image(self, arg):
        self.__handler.on_screen_image(image=arg.value)
        return None

    def action_monitor_target_status(self, arg):
        v = _STATUS_IN == arg.value
        self.__handler.on_screen_target_status(target_is_in=v)
        self.__fsm.event("monitor_target_status", v)
        return None

    def action_check_upstream(self, arg):
        self.__upstream = _Upstream(self, arg)
        return None

    def action_move_target(self, arg):
        if self.__target_control:
            self.__target_control = self.accessor("target_control")
        self.__target_control.put(_MOVE_TARGET_IN[arg.want_in])

    def action_req_move_target(self, arg):
        self.__fsm.event("move_target", arg)
        return None

    def req_action(self, method, arg):
        """Called by DeviceScreen which has separate life cycle"""
        if self.destroyed:
            raise AssertionError("already destroyed")
        self.action(method, arg)

    def _destroy(self):
        if self.__upstream:
            (u, self.__upstream) = (self.__upstream, None)
            u.destroy()

    def __handle_monitor(self, **kwargs):
        a = PKDict(kwargs)
        if "error" in arg:
            self.action(self.action_monitor_error, arg)
        elif "connected" in arg:
            pass
        else:
            self.action(getattr(self, f"action_monitor_{a.accessor.accessor_name}"), a)

    def _loop(self, *args, **kwargs):
        for a in "acquire", "image", "target_status":
            self.accessor(a).monitor(self.__handle_monitor)
        super()._loop(*args, **kwargs)

    def _repr(self):
        return f"device={self.__device.device_name}"


_cfg = pykern.pkconfig.init(
    upstream_timeout_secs=(15, pykern.pkconfig.parse_seconds, "how long to wait for devices to return"),
)
