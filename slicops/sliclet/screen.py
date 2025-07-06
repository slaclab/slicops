"""Profile monitor Sliclet

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import slicops.sliclet
import pykern.util
import slicops.device
import slicops.device_db
import slicops.plot

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
)

_PLOT_ENABLE = (
    ("color_map.ui.enabled", True),
    ("color_map.ui.visible", True),
    ("curve_fit_method.ui.enabled", True),
    ("curve_fit_method.ui.visible", True),
    ("plot.ui.visible", True),
)


class Screen(slicops.sliclet.Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__device = None
        self.__monitors = PKDict()
        self.__single_button = False

    def handle_destroy(self):
        self.__device_destroy()

    def handle_ctx_set_camera(self, txn, changed, value, **kwargs):
        if changed:
            self.__device_change(txn, value)

    def handle_ctx_set_beam_path(self, txn, changed, value, **kwargs):
        if changed:
            self.__beam_path_change(txn, value)

    def handle_ctx_set_curve_fit_method(self, txn, changed):
        if changed:
            self.__update_plot()

    def handle_ctx_set_single_button(self, txn, **kwargs):
        self.__single_button = True
        self.__set_acquire(txn, 1)

    def handle_ctx_set_start_button(self, txn, **kwargs):
        self.__set_acquire(txn, 1)

    def handle_ctx_set_stop_button(self, txn, **kwargs):
        self.__set_acquire(txn, 0)

    def handle_start(self):
        with self.lock_for_update() as txn:
            # Disable all buttons except beam_path
            self.__beam_path_change(txn, None)

    def __beam_path_change(self, txn, value):
        def _choices():
            if value is None:
                return ()
            return slicops.device_db.device_names(value, _DEVICE_TYPE)

        c = txn.field_get("camera")
        txn.multi_set(
            ("camera.constraints.choices", _choices()),
            ("camera.value", None),
        )
        if value is None:
            txn.multi_set(
                _DEVICE_DISABLE
                + (("camera.ui.enabled", False), ("camera.ui.visible", False))
            )
        if txn.field_check("camera", c) is None:
            txn.field_set("camera", c)

    def __device_change(self, txn, camera):
        def _monitors():
            for n, h in (
                ("image", self.__handle_image),
                ("acquire", self.__handle_acquire),
            ):
                a = self.__device.accessor(n)
                m = self.__monitors[n] = _Monitor(a, h)
                a.monitor(m)

        def _setup():
            try:
                self.__device = self.__device = slicops.device.Device(camera)
                _monitors()
            except slicops.device.DeviceError as e:
                pkdlog(
                    "error={} setting up {}, clearing; stack={}", e, camera, pkdexc()
                )
                self.__device_destroy()
                # TODO(robnagler) not clear this is right
                raise pykern.util.APIError(e)

        self.__device_destroy()
        txn.multi_set(_DEVICE_DISABLE)
        if camera:
            _setup(c)
            txn.multi_set(_DEVICE_ENABLE + (("pv", self.__device.meta.pv_prefix),))

    def __device_destroy():
        if not self.__device:
            return
        self.__single_button = False
        for n, m in self.__monitors.items():
            m.destroy()
        self.__monitors = PKDict()
        try:
            self.__set_acquire(0)
        except Exception:
            pass
        try:
            self.__device.destroy()
        except Exception:
            pass
        self.__device = None

    def __handle_acquire(self, acquire):
        with self.lock_for_update() as txn:
            n = not acquire
            # Leave plot alone
            txn.multi_set(
                ("single_button.ui.enabled", n),
                ("stop_button.ui.enabled", n),
                ("stop_button.ui.enabled", acquire),
            )

    def __handle_image(self, image):
        with self.lock_for_update() as txn:
            if self.__update_plot(txn) and self.__single_button:
                self.__single_button = False
                self.__set_acquire(txn, 0)

    def __set_acquire(self, txn, acquire):
        if not self.__device:
            txn.multi_set(_BUTTONS_DISABLE)
            return
        v = self.__monitors.acquire.value
        if v is not None and v == acquire:
            # No button disable since nothing changed
            return
        # No presses until we get a response from device
        txn.multi_set(_BUTTONS_DISABLE)
        try:
            self.__device.put("acquire", acquire)
        except slicops.device.DeviceError as e:
            pkdlog(
                "error={} on {}, clearing camera; stack={}", e, self.__device, pkdexc()
            )
            raise pykern.util.APIError(e)

    def __update_plot(self, txn):
        if not self.__device:
            return False
        if not ((i := self.monitors.image.value) and i.size):
            return False
        if not txn.ui_get("plot", "enabled"):
            txn.multi_set(_PLOT_ENABLE)
        txn.field_set(
            "plot", slicops.plot.fit_image(image, txn.field_get("curve_fit_method"))
        )
        return True


CLASS = Screen


class _Monitor:
    # TODO(robnagler) handle more values besides plot
    def __init__(self, accessor, handler):
        self.__name = str(accessor)
        self.__destroyed = False
        self.__handler = handler
        self.value = None

    def destroy(self):
        self.__destroyed = True
        self.__handler = None
        self.value = None

    def __call__(self, change):
        if self.__destroyed:
            return
        if e := change.get("error"):
            pkdlog("error={} on {}", e, change.get("accessor"))
            return
        if (v := change.get("value")) is None:
            return
        self.value = v
        try:
            self.__handler(v)
        except Exception as e:
            pkdlog("handler error={} accessor={} stack={}", e, self.__name, pkdexc())
