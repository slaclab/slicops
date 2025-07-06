"""Profile monitor Sliclet

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import slicops.sliclet
import pykern.api.util
import pykern.util
import slicops.device
import slicops.device_db
import slicops.quest

_DEVICE_TYPE = "PROF"

_cfg = None


class Screen(slicops.sliclet.Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__device = None
        self.__monitor = None

    def handle_destroy(self):
        if self.__device:
            self.__device.destroy()
            self.__device = None
        if self.__monitor:
            self.__monitor.destroy()
            self.__monitor = None

    def ui_ctx_write_beam_path(self, txn):
        if txn.has_field_changed("beam_path"):
            self._beam_path_change(txn.field("beam_path"))

    def ui_ctx_write_start_button(self, value):
        self._set_acquire(1)
        self._button_setup(True)

    def ui_action_stop_button(self, value):
        self._set_acquire(0)
        self._button_setup(True)

    def _beam_path_change(self, value):
        # TODO(robnagler) get from device db
        self.put_fields_meta({
            #TODO(robnagler) updates context and if constraint doesn't
            #  match sets back to default or to None if nullable
            "camera.constraints.choices": slicops.device_db.device_names(value, _DEVICE_TYPE),
        })
        if (
            _validate_field(ux.camera, ux.camera.value) is not None
            or (o := ux.camera.value) is None
        ):
            return
        ux.camera.value = None
        self._device_change(ux, o)

    def _button_setup(self, ux, is_acquiring):
        if is_acquiring:
            ux.single_button.enabled = False
            ux.start_button.enabled = False
            ux.stop_button.enabled = True
        else:
            ux.single_button.enabled = True
            ux.start_button.enabled = True
            ux.stop_button.enabled = False

    def _device_change(self, old_name):
        def _acquiring(device):
            try:
                return device.get("acquire")
            except slicops.device.DeviceError as err:
                # does not return an error, the initial camera may not be currently available
                return False

        def _clear():
            # must be robust, used in "except:"
            self.put_field_values({pv: None})
            self._button_setup(False)

        def _destroy():
            if not old_name or not self.__device:
                return
            try:
                self._set_acquire(0)
            except Exception as e:
                pkdlog(
                    "set acquire=0 PV error={} device={} stack={}",
                    e,
                    self.__device.device_name,
                    pkdexc(),
                )
            self.__monitor.destroy()
            self.__monitor = None

        def _setup():
            d = None
            try:
                d = self.__device slicops.device.Device(ux.camera.value)
                ux.pv.value = d.meta.pv_prefix
                self._button_setup(ux, _acquiring(d))
                self.__monitor = _Monitor(self.__image_update)
                d.accessor("image").monitor(self.__monitor)
            except slicops.device.DeviceError as e:
                pkdlog("error={} on {}, clearing camera; stack={}", e, d, pkdexc())
                ux.camera.value = None
                _clear()
                raise pykern.util.APIError(e)

        _destroy()
        if ux.camera.value is None:
            _clear()
            return
        _setup()

CLASS = Screen


class _Monitor:
    # TODO(robnagler) handle more values besides plot
    def __init__(self, update):
        self.__destroyed = False
        self.__update = update
        self.plot = slicops.plot.Heatmap()

    def destroy(self):
        self.__destroyed = True
        self.__update = None
        self.plot = None

    def __call__(self, change):
        if self.__destroyed:
            return
        if e := change.get("error"):
            #TODO(robnagler) alert?
            pkdlog("error={} on {}", e, change.get("accessor"))
            return
        if (v := change.get("value")) is not None:
            self.plot.image = v
            self.__update()
