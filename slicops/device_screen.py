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
_CONTROL_REMOVE = 0
_CONTROL_INSERT = 1
_STATUS_IN = 2
_STATUS_OUT = 1

_BLOCKING_MSG = "upstream target is in"
_TIMEOUT_MSG = "upstream target status accessor timed out"


class DeviceScreen(slicops.device.Device):
    """Augment Device with screen specific operations"""

    def __init__(self, beam_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__worker = _Worker(self, beam_path)

    def destroy(self):
        self.__worker.destroy()
        super().destroy()

    def move_target(self, want_in, callback):
        self.__worker.req_action(
            self.action_req_move_target, PKDict(want_in=want_in, callback=callback)
        )

    def target_status(self, callback):
        self.__worker.req_action(self.work_req_target_status, PKDict(callback=callback))


class _FSM:
    def __init__(self, worker):
        self.worker = worker
        self.curr = PKDict(
            checking_target=False,
            target_is_in=None,
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

    def _event_move_target(self, arg):
        if self.curr.move_target is not None:
            raise AssertionError("already moving target")
        if self.curr.target_in == arg.want_in:
            return
        self.curr.move_target = arg
        if self.curr.target_in is None:
            self.event("check_target", None)
        elif arg.want_in:
            self.event("check_upstream", None)
        else:
            self.event("move_target_out", None)

    def _event_target_in(self, arg):
        curr.target = True
        if not (m := curr.move_target):
            return
        curr.move_target = None
        if m.want_in:
            self.curr.move_target = None
            m.callback(True)
        else:
            self.event("move_target", m)

    def _event_req_target_status(self, arg, checking_target, target_is_in, **kwargs):
        if target_is_in is not None:
            arg.callback(PKDict(target_is_in=self.curr.target))
            return
        if checking_target:
            # TODO(robnagler) don't crash here, but how to force callback to crash?
            arg.callback(PKDict(error="Already checking target"))
            return
        self.worker.action("check_target", arg)
        return PKDict(checking_target=True)


class _Thread:
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
                m, a = self.__actions.get(timeout=self._loop_timeout_secs)
                with self.__lock:
                    if self.destroyed:
                        return
                    m(a)
        except queue.Empty:
            self.action_loop_timeout()
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
            # TODO(robnagler) prefix with something?
            self.__problems[n] = e
        elif arg.value == _STATUS_IN:
            self.__problems[n] = _BLOCKING_MSG
        if not self.__devices:
            self.__done()

    def action_loop_timeout(self):
        for n in self.__devices:
            self.__problems[n] = _TIMEOUT_MSG
        # clear all devices but not destroying object itself
        self._destroy()
        self.__done()

    def _destroy(self):
        (d, self.__devices) = (self.__devices, PKDict())
        for x in d.values():
            x.destroy()

    def __done(self):
        self.__worker.action(
            self.work_upstream_status,
            PKDict(req_arg=self.__req_arg, problems=self.__problems)
        )
        # no devices so destroyed implicitly
        self.__destroyed = True

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

    def __init__(self, device, beam_path):
        self.__device = device
        self.__beam_path = beam_path
        self.__upstream = None
        self.__fsm = __FSM(self)
        self._loop_timeout_secs = 0
        super().__init__()

    def action_check_target(self, arg):
        if self.__upstream:
            raise AssertionError("already have upstream {} {}", self.__fsm, self.device)
        self.__upstream = _Upstream(self, arg)

    def action_req_move_target(self, arg):
        pass

    def action_req_target_status(self, arg):
        self.__fsm.event("req_target_status", arg)

    def req_action(self, method, arg):
        """Called by DeviceScreen which has separate life cycle"""
        if self.destroyed:
            raise AssertionError("already destroyed")
        self.action(method, arg)

    def _destroy(self):
        if self.__upstream:
            (u, self.__upstream) = (self.__upstream, None)
            u.destroy()

    def _repr(self):
        return f"device={self.__device.device_name}"


_cfg = pykern.pkconfig.init(
    upstream_timeout_secs=(15, pykern.pkconfig.parse_seconds, "how long to wait for devices to return"),
)
