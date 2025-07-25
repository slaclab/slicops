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


class Screen(slicops.device.Device):

    def __init__(self, beam_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beam_path = beam_path
        # rjn there are a lot of values here, which indicates a problem: too much scope for one object?
        self.__destroyed = False
        self.__value = None
        self.__work_q = queue.Queue()
        self.__lock = threading.Lock()
        self.__control_lock = False
        self.__status_accessor = None
        self.__worker = threading.Thread(
            target=self.__work,
            args=(self.device_name, self.__work_q, self.__lock),
        )
        n = self._upstream_names()
        # The following line has to come before __status.monitor. Why?
        # rjn you always need to initialize an object before starting threads
        self.__worker.start()
        # rjn if the target is already in, then we don't need to check monitors
        # rjn so let's defer this operation until we need it.

    # rjn refrain from getters. unit tests are not blackbox so they can reach inside
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
            pkdlog("error={} accessor={} stack={}", e, name, pkdexc(simplify=True))
        finally:
            super().destroy()

    # rjn i think this would be embedded in a single function since get_complete blocks anyway
    # rjn however, at this point, i think we want to integrate in sliclet/screen so we can
    # rjn have a driver for the api we are creating. i suspect we'll want it to work a lot
    # rjn like image and acquire
#rjn don't need
    def get_status_async(self):
        with self.__lock:
            self.__work_q.put_nowait((_Work.get, None))

#rjn don't need
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

    def move_target(self, want_in, callback):
        """Check beam, unblock upstream, move target
        """
        with self.__lock:
            self._assert_control_unlock()
            # rjn this is when we lock so we make sure the caller doesn't call this twice
            self.__control_lock = True
            self.__work_q.put_nowait(
                PKDict(op=self.__work_control, want_in=want_in, callback=callback),
            )

    def unblock_upstream(self):
        # rjn i think this is where we want to do work in the thread
        # rjn there's a user interface question here:
        # rjn  do we want to just have the user try to move the target
        # rjn  and present a popup when there are blocking upstream devicesb
        # rjn  then the user would get to respond abort/retry/ignore and
        # rjn  sliclet/screen would handle appropriately. there are times
        # rjn  when it's ok for the target to get moved (beam off) without checking targets
        # rjn  in fact we may want that in here too, that is we check beam on/off
        # rjn  first, because that's the most critical operation. if the beam is on
        # rjn  i don't think we allow them to move the target without an are you sure at least
        # rjn  popups are a thing we have to add to vue, but that should be easy
        with self.__lock:
            self._assert_control_unlock()
            # rjn there's a race condition here. we need to consider the
            # rjn owner of the lock. i think what should be done is this
#            self.__work_q.put_nowait((_Work.upstream_out, q := queue.Queue()))
#        who owns the lock here

        # rjn            self.__control_lock = False
        # rjn what if we could not unblock the upstream. this probably wants a result
        # rjn we want a timeout i think
        v = q.wait(timeout=N)
        with self.__lock:
            if self.__destroyed:
                raise ValueError(f"destroyed device={self.device_name}")

    # rjn this should be done as soon as control_done is set
    #            self.__control_lock = False
    #            self.__control_done.clear()


    def _assert_control_unlock(self):
        if self.__control_lock:
            raise DeviceError(f"command already issued with device={self.device_name}")
        # rjn not sure this is right here.
        if self.__control_done.is_set():
            raise DeviceError(f"control did not complete on device={self.device_name}")

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

    def _state_target_out(self, event):
        event.arg.callback(TARGET_OUT)

    def _state_target_status_unknown(self, event):
        self.__status_accessor = self.accessor("target_status")
        self.__control_accessor = self.accessor("target_control")
        self.__last_status = None
        self.__status_accessor.monitor(self.__handle_status)
        self.__state.event("monitoring_status", event.arg)

    def _state_target():
        # check status
        if self.__status_accessor is None:
            self.__init_status()
#            self.__work_q.put_nowait(PKDict(op=self.__
        # check beam
        if work.want_in:
            pass # check upstream
        self.__control.put(_IN if work.want_in else _OUT)


    def __work_move_target(self, work):
        if target status unknown:
            wait status was known


        self.__state.event("move_target_in" if work.want_in "move_target_out", work)


    def __work_control(self, work):
        # Do epics
        self.__control.put(v)
        self.__control_lock = True

    def __work_get(self):
        self.__last_status = self.__control.get(v)
        self.__get_complete.set()

    def __work_status(self, value):
        if value == _IN:
            if self.__control_lock:
                self.__control_done.set()
        elif value == _OUT:
            if self.__control_lock:
                self.__control_done.set()
        else:
            pkdlog("WARNING: unexpected value={}", value)
    def __work_handle_status(self, value):
        with self.__lock:
            if self.__destroyed:
                return
            c = self.__client.handle_screen_status
        c(value)

    def __work_upstream(self):
        if len(self.__blocking_devices) == 0:
            if self.__control_lock:
            self.__control_done.set()

    def __work_upstream(self):
        # rjn since you are pulling out the screen here, it seems
        # rjn that this logic could be in _Upstream.handle_status
        # We want a threaded solution instead?
        for n in self.__blocking_devices:
            # rjn definitely needs to be async
            u = self.__upstream_devices.get(n)
            u.target_out()
        self.__control_lock = True

    def __handle_status(self, value):
        with self.__lock:
            if self.__destroyed:
                return
            self.__work_q.put_nowait(PKDict(op=self.__work_handle_status, value=value))

    def _handle_upstream_status(self, upstream, value):
        with self.__lock:
            if self.__destroyed:
                return
            # rjn i think "is" incorrect. "value" is coming from epics
            # rjn and _IN is defined internally so _IN only works here
            # rjn if _IN is an int or bool. If it were an enum, i don't think it would work.
            if value == _IN:
                self.__blocking_devices.add(upstream)
            if value is _OUT:
                # rjn self.__blocking_devices.discard(upstream)
                self.__blocking_devices.discard(upstream)
            self.__work_q.put_nowait((_Work.upstream, None))

    def __init_upstream(self):
        def _upstream_names():
            return slicops.device_db.upstream_devices(
                "PROF", "target_control", self.beam_path, self.device_name
            )

        self.__blocking_devices = set()
        self.__upstream_devices = PKDict({u: _UpstreamScreen(self, u) for u in _upstream_names()})

    def _upstream_monitor(self):

        for n, s in self.__upstream_devices.items():
            s.start_monitor()


class _Event:
    def __init__(self, event, arg):
        self.event = self.__assert_event(event)
        self.arg = arg
        self.old_state = _state
        self.new_state = self._next_state()

    def __assert_event(self, value):
        if value in self._EVENTS:
            return value;
        raise AssertionError(f"invalid event={value}")

    def __assert_state(self, value):
        if value in self._STATES:
            return value;
        raise AssertionError(f"invalid state={value}")

    def _next_state(self):
        if rv := self._TRANSITIONS[self._oldState][self._event]:
            return rv;
        raise AssertionError(f"invalid transition oldState={self._old_state} event={self._event}")

class _State:
    def __init__(self):
        self.beam = None
        self.target = None
        self.upstream = None
        self.acquire = None
        self.event = None

    def on_change_target(self, value):
        if value == _IN:
            self.target = True
            how does callback work
        elif value == _OUT:
            self.target = False
    def _event(self, name):
        if name == "target_status":
            if self.target is None:
                self.event_target_status()


    def event(self, event_name, work):
        e = _Event(self._state, event_name, work)
        self._state = e.new_state
        if h := getattr(self._device, f"_state_{self._new_state}", None):
            h(e)




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
        v = value.get("value")
        self.parent._handle_upstream_status(self.device.device_name, v)

    def destroy(self):
        with self.__lock:
            self.device.destroy()
