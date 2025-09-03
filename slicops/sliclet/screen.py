"""Profile monitor Sliclet

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import pykern.pkconfig
import pykern.util
import queue
import slicops.device
import slicops.device.screen
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
) + _BUTTONS_DISABLE

_DEVICE_ENABLE = (
    ("pv.ui.visible", True),
    ("single_button.ui.visible", True),
    ("start_button.ui.visible", True),
    ("stop_button.ui.visible", True),
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

# Target Controls
_CTL_OUT = 0
_CTL_IN = 1
_STS_OUT = 1
_STS_IN = 2


class Screen(slicops.sliclet.Base):
    def __init__(self, *args):
        self.__prev_value = PKDict(acquire=None, image=None)
        super().__init__(*args)

    def handle_destroy(self):
        self.__device_destroy()

    def on_change_camera(self, txn, value, **kwargs):
        self.__device_change(txn, txn.field_get("beam_path"), value)

    def on_change_beam_path(self, txn, value, **kwargs):
        self.__beam_path_change(txn, value)

    def on_change_curve_fit_method(self, txn, **kwargs):
        self.__update_plot(txn)

    def on_click_single_button(self, txn, **kwargs):
        self.__single_button = True
        self.__set_acquire(txn, True)

    def on_click_start_button(self, txn, **kwargs):
        self.__set_acquire(txn, True)

    def on_click_stop_button(self, txn, **kwargs):
        self.__set_acquire(txn, False)

    def on_click_target_in_button(self, txn, **kwargs):
        self.__set_target(txn, _CTL_IN)

    def on_click_target_out_button(self, txn, **kwargs):
        self.__set_target(txn, _CTL_OUT)

    def handle_init(self, txn):
        self.__device = None
        self.__handler = None
        self.__single_button = False
        txn.multi_set(("beam_path.constraints.choices", slicops.device_db.beam_paths()))
        self.__beam_path_change(txn, None)
        self.__device_change(txn, None, None)
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
        self.__device_setup(txn, txn.field_get("beam_path"), txn.field_get("camera"))

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
            self.__device_change(txn, value, None)

    def __device_change(self, txn, beam_path, camera):
        self.__device_destroy(txn)
        txn.multi_set(_DEVICE_DISABLE)
        if camera and beam_path:
            self.__device_setup(txn, beam_path, camera)

    def __device_destroy(self, txn=None):
        if not self.__device:
            return
        self.__single_button = False
        self.__handler.destroy()
        self.__handler = None
        try:
            n = self.__device.device_name
        except Exception:
            n = None
        try:
            self.__device.destroy()
        except Exception as e:
            pkdlog("destroy device={} error={}", n, e)
        self.__device = None

    def __device_setup(self, txn, beam_path, camera):
        self.__handler = _Handler(
            self.__handle_worker_error,
            self.__handle_device_error,
            PKDict(
                image=self.__handle_image,
                acquire=self.__handle_acquire,
                target_status=self.__handle_target,
            ),
        )
        try:
            # If there's an epics issues, we have to clear the device
            self.__device = slicops.device.screen.Screen(
                beam_path,
                camera,
                self.__handler,
            )
        except slicops.device.DeviceError as e:
            pkdlog("error={} setting up {}, clearing; stack={}", e, camera, pkdexc())
            self.__device_destroy(txn)
            self.__user_alert(txn, "unable to connect to camera={} error={}", camera, e)
            return
        txn.multi_set(_DEVICE_ENABLE + (("pv.value", self.__device.meta.pv_prefix),))

    def __handle_acquire(self, acquire):
        with self.lock_for_update() as txn:
            self.__prev_value["acquire"] = acquire
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

    def __handle_device_error(self, accessor_name, error_kind, error_msg):
        pkdlog(f"error={error_kind} accessor={accessor_name} msg={error_msg}")

    def __handle_image(self, image):
        with self.lock_for_update() as txn:
            self.__prev_value["image"] = image
            if self.__update_plot(txn) and self.__single_button:
                # self.__single_button = False
                self.__set_acquire(txn, False)
                txn.multi_set(
                    ("single_button.ui.enabled", True),
                    ("start_button.ui.enabled", True),
                )

    def __handle_target(self, status):
        with self.lock_for_update() as txn:
            msg = "In" if status else "Out"
            txn.field_set("target_status", msg)

    def __handle_worker_error(self, exception):
        self.put_error(exception)

    def __set_acquire(self, txn, acquire):
        if not self.__device or not self.__handler:
            # buttons already disabled
            return
        v = self.__prev_value["acquire"]
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

    def __set_target(self, txn, target):
        try:
            self.__device.move_target(want_in=bool(target))
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
    def __update_plot(self, txn):
        if not self.__device or not self.__handler:
            return False
        # TOOD Change previous value to current value (nominally).
        if (i := self.__prev_value["image"]) is None or not i.size:
            return False
        if not txn.group_get("plot", "ui", "visible"):
            txn.multi_set(_PLOT_ENABLE)
        txn.field_set(
            "plot",
            slicops.plot.fit_image(i, txn.field_get("curve_fit_method")),
        )
        return True

    def __user_alert(self, txn, fmt, *args):
        pkdlog("TODO: USER ALERT: " + fmt, *args)


CLASS = Screen


class _Handler(slicops.device.screen.EventHandler):
    def __init__(
        self,
        handle_worker_error,
        handle_device_error,
        handle_device_update,
    ):
        self.__destroyed = False
        self.__lock = threading.Lock()
        self.__handle_worker_error = handle_worker_error
        self.__handle_device_error = handle_device_error
        self.__handle_device_update = handle_device_update

    def destroy(self):
        with self.__lock:
            if self.__destroyed:
                return
            self.__destroyed = True
            self.__handle_device_error = None
            self.__handle_device_update = None

    def on_screen_worker_error(self, exception):
        self.__handle_worker_error(exception)

    def on_screen_device_error(self, accessor_name, error_kind, error_msg):
        self.__handle_device_error(accessor_name, error_kind, error_msg)

    def on_screen_device_update(self, accessor_name, value):
        # TODO move prev value to sliclet within txn
        if not accessor_name in self.__handle_device_update:
            raise AssertionError(f"unsupported accessor={n} {self}")
        h = self.__handle_device_update[accessor_name]
        h(value)


def _init():
    global _cfg

    _cfg = pykern.pkconfig.init(
        dev=PKDict(
            beam_path=("DEV_BEAM_PATH", str, "dev beam path name"),
            camera=("DEV_CAMERA", str, "dev camera name"),
        ),
    )


_init()
