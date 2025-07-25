"""Accessing meta data about devices

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

_REMOVE = 0
_INSERT = 1
_IN = 2
_OUT = 1


class Screen(slicops.device.Device):

    def __init__(self, beam_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beam_path = beam_path
        self.__destroyed = False
        self.__value = None
        self.__work_q = queue.PriorityQueue()
        self.__lock = threading.Lock()
        self.__upstream_devices = {}
        self.__status = self.accessor("target_status")
        self.__control = self.accessor("target_control")
        self.__blocking_devices = set()
        self.__get_complete = threading.Event()
        self.__control_lock = False
        self.__control_done = threading.Event()
        self.__last_status = None
        self.__worker = threading.Thread(
            target=self.__work,
            args=(self.device_name, self.__work_q, self.__lock),
        )
        n = self._upstream_names()
        # The following line has to come before __status.monitor. Why?
        self.__upstream_devices = self._get_upstream_devices(n)
        self.__worker.start()
        self.__status.monitor(self.__handle_status)
        self._upstream_monitor()

    def blocking_devices(self):
        return self.__blocking_devices

    def upstream_devices(self):
        return self.__upstream_devices

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
            pkdlog("error={} accessor={} stack={}", e, name, pkdexc())
        finally:
            super().destroy()

    def get_status_async(self):
        with self.__lock:
            self.__work_q.put_nowait((_Work.get, None))

    def get_status_complete(self):
        with self.__lock:
            if self.__destroyed:
                raise ValueError(f"destroyed device={self.device_name}")
            c = self.__get_complete
        c.wait()
        with self.__lock:
            if self.__last_status is None:
                raise ValueError(f"device={self.device_name} got no status.")
            self.__get_complete.clear()
        return self.__last_status

    def insert_target(self):
        self._move_target(_INSERT)

    def remove_target(self):
        self._move_target(_REMOVE)

    def unblock_upstream(self):
        with self.__lock:
            self._assert_control_unlock()
            self.__work_q.put_nowait((_Work.upstream_out, None))
            t = self.__control_done
        t.wait()
        with self.__lock:
            if self.__destroyed:
                raise ValueError(f"destroyed device={self.device_name}")
            self.__control_lock = False
            self.__control_done.clear()

    def _move_target(self, position):
        with self.__lock:
            self._assert_control_unlock()
            self.__work_q.put_nowait((_Work.control, position))
            t = self.__control_done
        t.wait()
        with self.__lock:
            if self.__destroyed:
                raise ValueError(f"destroyed device={self.device_name}")
            self.__control_lock = False
            self.__control_done.clear()

    def _assert_control_unlock(self):
        if self.__control_lock:
            raise DeviceError(
                f"command already issued with device={self.device_name}"
            )
        if self.__control_done.is_set():
            raise DeviceError(
                f"control did not complete on device={self.device_name}"
            )

    def __work(self, name, work_q, lock):
        try:
            while True:
                w, v = work_q.get()
                with lock:
                    if self.__destroyed:
                        return
                    if _Work.control == w:
                        self.__control.put(v)
                        self.__control_lock = True
                        continue
                    if _Work.get == w:
                        self.__last_status = self.__control.get(v)
                        self.__get_complete.set()
                        continue
                    if _Work.status == w:
                        if v == _IN:
                            if self.__control_lock:
                                self.__control_done.set()
                        elif v == _OUT:
                            if self.__control_lock:
                                self.__control_done.set()
                        continue
                    if _Work.upstream == w:
                        if len(self.__blocking_devices) == 0:
                            if self.__control_lock:
                                self.__control_done.set()                            
                        continue
                    if _Work.upstream_out == w:
                        # We want a threaded solution instead?
                        for n in self.__blocking_devices:
                            u = self.__upstream_devices.get(n)
                            u.target_out()
                        self.__control_lock = True
                        continue
                    raise AssertionError(f"unknown work={w}")
        except Exception as e:
            pkdlog("error={} accessor={} stack={}", e, name, pkdexc())
        finally:
            self.destroy()

    def __handle_status(self, work):
        with self.__lock:
            if self.__destroyed:
                return
            if e := work.get("error"):
                pkdlog("error={} on {}", e, work.get("accessor"))
                return
            if (v := work.get("value")) is None:
                return
            self.__work_q.put_nowait((_Work.status, v))

    def _handle_upstream_status(self, upstream, value):
        with self.__lock:
            if self.__destroyed:
                return
            if value is _IN:
                self.__blocking_devices.add(upstream)
            if value is _OUT:
                if upstream in self.__blocking_devices:
                    self.__blocking_devices.remove(upstream)
            self.__work_q.put_nowait((_Work.upstream, None))

    def _upstream_names(self):
        return slicops.device_db.upstream_devices(
            "PROF",
            "target_control",
            self.beam_path,
            self.device_name
        )

    def _get_upstream_devices(self, upstream_devices):
        return PKDict({u: _UpstreamScreen(self, u) for u in upstream_devices})

    def _upstream_monitor(self):
        for n, s in self.__upstream_devices.items():
            s.start_monitor()

    

class _Work(enum.IntEnum):
    # sort in priority value order, lowest number is highest priority
    # This is getting unwieldy. How to make functions w/ priority?
    destroy = 0
    status = 1
    upstream = 2
    get = 3
    control = 4
    upstream_out = 5

class _UpstreamScreen:
    def __init__(self, parent, device_name):
        self.device = slicops.device.Device(device_name)
        self.parent = parent
        self.status = self.device.accessor("target_status")
        self.__lock = threading.Lock()

    def start_monitor(self):
        # _UpstreamScreen must exist before monitor so it can be destroyed.
        self.status.monitor(self.__handle_status)

    def target_out(self):
        with self.__lock:
            a = self.device.accessor("target_control")
            a.put(_REMOVE)

    def __handle_status(self, value, **kwargs):
        v = value.get('value')
        self.parent._handle_upstream_status(self.device.device_name, v)

    def destroy(self):
        with self.__lock:
            self.device.destroy()
