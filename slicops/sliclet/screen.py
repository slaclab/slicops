"""Profile monitor Sliclet

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from datetime import datetime
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import h5py
import numpy
import pykern.pkcompat
import pykern.pkconfig
import pykern.util
import queue
import slicops.device
import slicops.device_db
import slicops.plot
import slicops.sliclet
import threading

_DEVICE_TYPE = "PROF"

_cfg = None

_BUTTONS_DISABLE = (
    ("single_button.ui.enabled", False),
    ("stop_button.ui.enabled", False),
    ("start_button.ui.enabled", False),
)

_DEVICE_DISABLE = (
    ("color_map.ui.enabled", False),
    ("color_map.ui.visible", False),
    ("curve_fit_method.ui.enabled", False),
    ("curve_fit_method.ui.visible", False),
    ("plot.ui.visible", False),
    # Useful to avoid large ctx sends
    ("plot.value", None),
    ("pv.ui.visible", False),
    ("pv.value", None),
    ("single_button.ui.visible", False),
    ("start_button.ui.visible", False),
    ("stop_button.ui.visible", False),
    ("save_button.ui.visible", False),
    ("n_average.ui.visible", False),
    ("save_button.ui.enabled", False),
) + _BUTTONS_DISABLE

_DEVICE_ENABLE = (
    ("pv.ui.visible", True),
    ("single_button.ui.visible", True),
    ("start_button.ui.visible", True),
    ("stop_button.ui.visible", True),
    ("save_button.ui.visible", True),
    ("n_average.ui.visible", True),
    ("single_button.ui.enabled", True),
    ("stop_button.ui.enabled", False),
    ("start_button.ui.enabled", True),
)

_PLOT_ENABLE = (
    ("color_map.ui.enabled", True),
    ("color_map.ui.visible", True),
    ("curve_fit_method.ui.enabled", True),
    ("curve_fit_method.ui.visible", True),
    ("plot.ui.visible", True),
)


class Screen(slicops.sliclet.Base):
    def handle_destroy(self):
        self.__device_destroy()

    def on_change_beam_path(self, txn, value, **kwargs):
        self.__beam_path_change(txn, value)

    def on_change_camera(self, txn, value, **kwargs):
        self.__device_change(txn, value)

    def on_change_curve_fit_method(self, txn, value, **kwargs):
        # TODO(robnagler) optimize with ImageSet.update_curve_fit_method()
        self.__new_image_set(txn)

    def on_change_n_average(self, txn, value, **kwargs):
        # TODO(robnagler) optimize with ImageSet.update_n_average()
        self.__new_image_set(txn)

    def on_click_save_button(self, txn, **kwargs):
        self.__image_set.save_file(self.save_file_path())

    def on_click_single_button(self, txn, **kwargs):
        self.__single_button = True
        self.__set_acquire(txn, True)

    def on_click_start_button(self, txn, **kwargs):
        self.__set_acquire(txn, True)

    def on_click_stop_button(self, txn, **kwargs):
        self.__set_acquire(txn, False)

    def handle_init(self, txn):
        self.__device = None
        self.__monitors = PKDict()
        self.__single_button = False
        txn.multi_set(("beam_path.constraints.choices", slicops.device_db.beam_paths()))
        self.__beam_path_change(txn, None)
        self.__device_change(txn, None)
        b = c = None
        if pykern.pkconfig.in_dev_mode():
            b = _cfg.dev.beam_path
            c = _cfg.dev.camera
        # the values are None by default, but this initializes
        # the state of the choices, buttons and fields appropriately
        txn.field_set("beam_path", b)
        self.__beam_path_change(txn, b)
        txn.field_set("camera", c)

    def handle_start(self, txn):
        self.__device_setup(txn, txn.field_get("camera"))

    def __beam_path_change(self, txn, value):
        def _choices():
            if value is None:
                return ()
            return slicops.device_db.device_names(_DEVICE_TYPE, value)

        txn.multi_set(
            ("camera.constraints.choices", _choices()),
            ("camera.value", None),
        )
        # This technically shouldn't happen
        if value is None:
            txn.multi_set(
                _DEVICE_DISABLE
                + (("camera.ui.enabled", False), ("camera.ui.visible", False))
            )
        else:
            txn.multi_set((("camera.ui.enabled", True), ("camera.ui.visible", True)))
        if not self.__device:
            # No device change
            return
        c = self.__device.device_name
        if txn.is_field_value_valid("camera", c):
            # Camera is the same so restore the value, no device change
            txn.field_set("camera", c)
        else:
            self.__device_change(txn, None)

    def __device_change(self, txn, camera):
        self.__device_destroy(txn)
        txn.multi_set(_DEVICE_DISABLE)
        if camera:
            self.__device_setup(txn, camera)

    def __device_destroy(self, txn=None):
        if not self.__device:
            return
        self.__image_set = None
        self.__single_button = False
        for m in self.__monitors.values():
            m.destroy()
        self.__monitors = PKDict()
        try:
            n = self.__device.device_name
        except Exception:
            n = None
        try:
            self.__device.destroy()
        except Exception as e:
            pkdlog("destroy device={} error={}", n, e)
        self.__device = None

    def __device_setup(self, txn, camera):
        def _monitors():
            for n, h in (
                ("image", self.__handle_image),
                ("acquire", self.__handle_acquire),
            ):
                a = self.__device.accessor(n)
                m = self.__monitors[n] = _Monitor(a, h)
                a.monitor(m)

        try:
            # If there's an epics issues, we have to clear the device
            self.__device = self.__device = slicops.device.Device(camera)
            _monitors()
        except slicops.device.DeviceError as e:
            pkdlog("error={} setting up {}, clearing; stack={}", e, camera, pkdexc())
            self.__device_destroy(txn)
            self.__user_alert(txn, "unable to connect to camera={} error={}", camera, e)
            return
        txn.multi_set(_DEVICE_ENABLE + (("pv.value", self.__device.meta.pv_prefix),))
        self.__new_image_set(txn)

    def __handle_acquire(self, acquire):
        with self.lock_for_update() as txn:
            n = not acquire
            # Leave plot alone
            txn.multi_set(
                ("single_button.ui.enabled", n),
                ("start_button.ui.enabled", n),
                (
                    "stop_button.ui.enabled",
                    acquire and not self.__single_button,
                ),
            )
            if not acquire:
                self.__single_button = False

    def __handle_image(self, image):
        def _plot(txn):
            if not self.__device:
                return False
            if (i := self.__monitors.image.prev_value()) is None or not i.size:
                return False
            if (
                p := self.__image_set.add_frame(image, pykern.pkcompat.utcnow())
            ) is None:
                return False
            if not txn.group_get("plot", "ui", "visible"):
                txn.multi_set(_PLOT_ENABLE)
            txn.field_set("plot", p)
            if not txn.group_get("save_button", "ui", "enabled"):
                txn.multi_set(("save_button.ui.enabled", True))
            return True

        with self.lock_for_update() as txn:
            if _plot(txn) and self.__single_button:
                self.__set_acquire(txn, False)
                txn.multi_set(
                    ("single_button.ui.enabled", True),
                    ("start_button.ui.enabled", True),
                )

    def __new_image_set(self, txn):
        self.__image_set = slicops.plot.ImageSet(
            txn.multi_get(("beam_path", "camera", "curve_fit_method", "n_average", "pv")),
        )

    def __set_acquire(self, txn, acquire):
        if not self.__device:
            # buttons already disabled
            return
        v = self.__monitors.acquire.prev_value()
        if v is not None and v == acquire:
            # No button disable since nothing changed
            return
        if txn:
            # No presses until we get a response from device
            txn.multi_set(_BUTTONS_DISABLE)
        try:
            self.__device.put("acquire", acquire)
        except slicops.device.DeviceError as e:
            pkdlog(
                "error={} on {}, clearing camera; stack={}", e, self.__device, pkdexc()
            )
            raise pykern.util.APIError(e)

    #    def __target_moved(self, status):
    #        if status is failed:
    #            display error
    #        if status is out:
    #            disable buttons
    #        if status is in:
    #            enable buttons
    #
    def __user_alert(self, txn, fmt, *args):
        pkdlog("TODO: USER ALERT: " + fmt, *args)


CLASS = Screen


class _Monitor:
    # TODO(robnagler) handle more values besides plot
    def __init__(self, accessor, handler):
        self.__name = str(accessor)
        self.__destroyed = False
        self.__handler = handler
        self.__value = None
        self.__change_q = queue.Queue(1)
        self.__lock = threading.Lock()
        self.__thread = threading.Thread(
            target=self.__dispatch,
            daemon=True,
            # Reduce the places where locking needs to occur
            args=(self.__name, self.__change_q, self.__lock, self.__handler),
        )
        self.__thread.start()

    def destroy(self):
        with self.__lock:
            if self.__destroyed:
                return
            self.__destroyed = True
            try:
                # if there is an exception, ignore it because the queue already has an item for wakeup dispatch
                self.__change_q.put_nowait(False)
            except Exception:
                pass
            # cause callers to crash
            try:
                delattr(self, "value")
            except Exception:
                pass

    def prev_value(self):
        with self.__lock:
            if self.__destroyed:
                return
            return self.__value

    def __call__(self, change):
        with self.__lock:
            if self.__destroyed:
                return
            if e := change.get("error"):
                pkdlog("error={} on {}", e, change.get("accessor"))
                return
            if (v := change.get("value")) is None:
                return
            try:
                self.__change_q.put_nowait(v)
            except queue.Full:
                if self.__change_q.get_nowait() is not None:
                    self.__change_q.task_done()
                # puts are locked
                self.__change_q.put_nowait(v)

    def __dispatch(self, name, change_q, lock, handler):
        try:
            while True:
                v = change_q.get()
                change_q.task_done()
                with lock:
                    if self.__destroyed:
                        return
                    self.__value = v
                try:
                    handler(v)
                except Exception as e:
                    # Touches self.__name which should not be modified
                    pkdlog("handler error={} accessor={} stack={}", e, name, pkdexc())
        except Exception as e:
            pkdlog("error={} accessor={} stack={}", e, name, pkdexc())
        finally:
            self.destroy()


def _init():
    global _cfg

    _cfg = pykern.pkconfig.init(
        dev=PKDict(
            beam_path=("DEV_BEAM_PATH", str, "dev beam path name"),
            camera=("DEV_CAMERA", str, "dev camera name"),
        ),
    )


_init()
