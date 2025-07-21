"""Accessing meta data about devices

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
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

    def __init__(self, beamline=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__beamline = beamline
        self.__destroyed = False
        self.__value = None
        self.__work_q = queue.PriorityQueue()
        self.__lock = threading.Lock()
        self.__status = self.accessor("target_status")
        self.__control = self.accessor("target_control")
        self.__target_in = threading.Event()
        self.__target_out = threading.Event()
        self.__worker = threading.Thread(
            target=self.__work,
            args=(self.device_name, self.__work_q, self.__lock),
        )
        self.__worker.start()
        self.__status.monitor(self.__handle_status)

    def destroy(self):
        try:
            with self.__lock:
                if self.__destroyed:
                    return
                self.__destroyed = True
                self.__work_q.put_nowait((_Work.destroy, None))
                self.__work_q = None
                self.__target_in.set()
                # cause callers to crash
                try:
                    delattr(self, "value")
                except Exception:
                    pass
        finally:
            super().destroy()

    def _get_upstream(self):
        if self.beam_line is None:
            return None
        upstream_names = slicops.device_db.upstream_devices(
            "PROF",
            "target_control",
            self.beam_path,
            self.device_name
        )
        return {
            name: slicops.device.Device(name) for n in upstream_names
        }

    def insert_target(self):
        with self.__lock:
            if self.__target_in.is_set():
                return
            self.__work_q.put_nowait((_Work.control, _INSERT))
            t = self.__target_in
        t.wait()
        with self.__lock:
            if self.__destroyed:
                raise ValueError(f"destroyed device={self.device_name}")

    def remove_target(self):
        with self.__lock:
            if self.__target_out.is_set():
                return
            self.__work_q.put_nowait((_Work.control, _REMOVE))
            t = self.__target_out
        t.wait()
        with self.__lock:
            if self.__destroyed:
p                raise ValueError(f"destroyed device={self.device_name}")

    def __work(self, name, work_q, lock):
        try:
            while True:
                w, v = work_q.get()
                with lock:
                    if self.__destroyed:
                        return
                    if _Work.control == w:
                        self.__control.put(v)
                        continue
                    if _Work.status == w:
                        if v == _IN:
                            self.__target_in.set()
                            self.__target_out.clear()
                        elif v == _OUT:
                            self.__target_in.clear()
                            self.__target_out.set()
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


class _Work(enum.IntEnum):
    # sort in priority value order, lowest number is highest priority
    destroy = 0
    status = 1
    control = 2

#    = slicops.device_db.upstream_devices(device_name)
