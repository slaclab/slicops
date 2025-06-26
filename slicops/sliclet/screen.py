"""Profile monitor Sliclet

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import slicops.sliclet
import pykern.pkio
import numpy
import pykern.api.util
import pykern.util
import scipy.optimize
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

    def destroy(self):
        if self.__monitor:
            self.__monitor.destroy()
            self.__monitor = None
        if self.__device:
            self.__device.destroy()
            self.__device = None

    def ui_action_beam_path(self, new_value, old_value):
        if new_value != old_value:
            self._beam_path_change(value)

    def ui_action_start_button(self, value):
        self._set_acquire(1)
        self._button_setup(True)

    def ui_action_stop_button(self, value):
        self._set_acquire(0)
        self._button_setup(True)

    def _beam_path_change(self, ux, old_name):
        # TODO(robnagler) get from device db
        ux.camera.choices = _choice_map(
            slicops.device_db.device_names(ux.beam_path.value, _DEVICE_TYPE),
        )
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
            self.update_fields({pv: None})
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
                self.__monitor = _Monitor(self)
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
    def __init__(self, sliclet):
        self._destroyed = False
        self._sliclet = sliclet
        self.plot = _Plot(sliclet)

    def __call__(self, change):
        if self._destroyed:
            return
        if e := change.get("error"):
            #TODO(robnagler) alert?
            pkdlog("error={} on {}", e, change.get("accessor"))
            return
        if (v := change.get("value")) is not None:
            self._update(v))

    def _update(self, image):
        try:
            self.__plot.new_image(image)
        except Exception as e:
            pkdlog("error={} stack={}", e, pkdexc())
            #TODO(robnagler) alert?
            raise


class _Plot:
    def __init__(self, sliclet):
        self.image = None
        self.sliclet = sliclet

    def new_image(self, image):
        self.image = image
        if self.image is None:
            self.sliclet.update_fields(plot=None)
            return
        self.sliclet.update_fields(plot=PKDict(
                raw_pixels=self.image,
                x=self._fit(ux, self.image.sum(axis=0)),
                y=self._fit(ux, self.image.sum(axis=1)[::-1]),
            ),
        )
        if not (ux.curve_fit_method.visible and ux.color_map.visible):
            update_fields
            ux.curve_fit_method.visible = True
            ux.color_map.visible = True
            rv.ui_ctx = ux
        return rv

    def _fit(self, ux, profile, count=0):
        """Use the scipy curve_fit() to match the selected method.
        Valid methods are (gaussian, super_gaussian).
        """

        def _fix(results):
            # sigma may be negative from the fit
            results.sig = abs(results.sig)
            return results

        def _gaussian(x, amplitude, mean, sigma, offset):
            return amplitude * numpy.exp(-(((x - mean) / sigma) ** 2) / 2) + offset

        def _super_gaussian(x, amplitude, mean, sigma, offset, p):
            return amplitude * numpy.exp(-numpy.abs((x - mean) / sigma) ** p) + offset

        popt = None
        dist_keys = ["amp", "mean", "sig", "offset"]
        # TODO(pjm): should use physical camera dimensions
        x = numpy.arange(len(profile))
        try:
            m = _gaussian
            popt, pcov = scipy.optimize.curve_fit(
                m,
                x,
                profile,
                p0=[
                    numpy.mean(profile),
                    len(profile) / 2,
                    len(profile) / 5,
                    numpy.min(profile),
                ],
            )
            if ux.curve_fit_method.value == "super_gaussian":
                # use gaussian fit to guess other distribution starting values
                m = _super_gaussian
                dist_keys.append("p")
                popt, pcov = scipy.optimize.curve_fit(
                    m, x, profile, p0=numpy.append(popt, 1.1)
                )
            elif ux.curve_fit_method.value != "gaussian":
                raise AssertionError(f"invalid fit method={ux.curve_fit_method.value}")
            fit_line = m(x, *popt)
        except RuntimeError as e:
            # TODO(pjm): show fitting error message on curve fit method field
            fit_line = numpy.zeros(len(x))
        return PKDict(
            lineout=profile,
            fit=PKDict(
                fit_line=fit_line,
                results=None if popt is None else _fix(PKDict(zip(dist_keys, popt))),
            ),
        )
