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

_BLOCKING = "blocking"


class Screen(slicops.device.Device):

    def __init__(self, beam_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beam_path = beam_path
        self.__destroyed = False
        self.__control_in_work = False
        self.__status_accessor = None

    def destroy(self):
        try:
            with self.__lock:
                if self.__destroyed:
                    return
                self.__destroyed = True
                self.__work_q.put_nowait((_Work.destroy, None))
                self.__work_q = None
                self.__control_done.set()
                for _, u in self.__upstream_devices.items():
                    u.destroy()
                # cause callers to crash
                try:
                    delattr(self, "value")
                except Exception:
                    pass
        except Exception as e:
            pkdlog("error={} accessor={} stack={}", e, name, pkdexc(simplify=True))
        finally:
            super().destroy()

    def move_target(self, want_in, callback):
        """Check beam, unblock upstream, move target"""
        with self.__lock:
            self.__fsm.event("move_target", PKDict(want_in=want_in, callback=callback))


class _Worker:
    def __init__(self, device):
        self.device = device
        self.__queue = queue.Queue()
        self.__lock = threading.Lock()
        self.__thread = threading.Thread(
            target=self.__do,
            args=(self.device.device_name, self.__work_q, self.__lock),
        )
        self.__thread.start()

    def __handle_upstream_status(self, problems):
        with self.__lock:
            if self.__destroyed:
                return
            if not problems:
                self.__state.event("upstream_clear", None)
            else:
                self.__state.event("upstream_problems", problems)

    def __work(self, name, work_q, lock):
        try:
            while True:
                w = work_q.get()
                with lock:
                    # rjn when there are this many if statements, move to dispatch
                    if self.__destroyed:
                        return
                    w.op(w)
        except Exception as e:
            pkdlog("error={} accessor={} stack={}", e, name, pkdexc())
        finally:
            self.destroy()


class _FSM:
    __SIMPLE = PKDict(
        target_in=PKDict(target=True),
        target_out=PKDict(target=False),
        upstream_clear=PKDict(upstream=True),
        upstream_problems=PKDict(upstream=False),
    )

    def __init__(self):
        self.curr = PKDict(
            beam=None, target=None, upstream=None, acquire=None, want_in=False
        )
        self.prev = self.curr.copy()

    def event(self, name, arg):
        self.prev = self.curr.copy()
        if t := self.___SIMPLE.get(name):
            self.curr.update(t)
        if t := getattr(self, f"_event_{name}"):
            t(arg)

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
        self.curr.target = True
        if not (m := self.curr.move_target):
            return
        self.curr.move_target = None
        if m.want_in:
            self.curr.move_target = None
            m.callback(True)
        else:
            self.event("move_target", m)


class _Upstream:
    def __init__(self, parent):
        def _names():
            return slicops.device_db.upstream_devices(
                "PROF", "target_control", parent.beam_path, parent.device_name
            )

        self.__parent = parent
        self.__destroyed = False
        # Allows calling destroy in __handle_status
        self.__lock = threading.Lock()
        self.__problems = PKDict()
        self.__devices = PKDict({u: slicops.device.Device(u) for u in _names()})

    def check(self):
        for n, d in self.__devices.items():
            d.accessor("target_status").monitor(self.__handle_status)

    def destroy(self):
        with self.__lock:
            if self.__destroyed:
                return
            self.__destroyed = True
            for d in self.__devices.values():
                d.destroy()

    def __handle_status(self, **kwargs):
        with self.__lock:
            n = kwargs["accessor"].device.device_name
            self.__devices.pkdel(n).destroy()
            if e := kwargs.get("error"):
                pkdlog("device={} error={}", n, e)
                self.__problems[n] = e
            elif kwargs["value"] == "_IN":
                self.__problems[n] = _BLOCKING
            if not self.__devices:
                self.__parent._handle_upstream_status(self.__problems)
                # no devices so destroyed
                self.__destroyed = True
