"""Screen (Profile Monitor) implementation

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from lcls_tools.common.controls.pyepics.utils import PV, PVInvalidError
from pykern import pkconfig
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import lcls_tools.common.data.fitting_tool
import lcls_tools.common.devices.reader
import numpy
import random
import slicops.quest
import slicops.ui_schema
import time

_NAME = "screen"

_API_PREFIX_LEN = len(f"api_{_NAME}_")

_NOT_API_WITH_FIELD = frozenset(
    ("ui_ctx", "stop_button", "single_button", "start_button")
)

_cfg = None

# TODO(pjm): needed to monkey path reader._device data to add a dev camera
_old_device_data = lcls_tools.common.devices.reader._device_data


def _monkey_patch_device_data(area=None, device_type=None, name=None):
    res = _old_device_data(area, device_type, name)
    res["screens"][_cfg.dev.camera_name] = {
        "controls_information": {
            "PVs": {
                "image": "13SIM1:image1:ArrayData",
                "n_col": "13SIM1:cam1:ArraySizeX_RBV",
                "n_row": "13SIM1:cam1:ArraySizeY_RBV",
                "n_bits": "13SIM1:cam1:N_OF_BITS",
                "resolution": "13SIM1:cam1:RESOLUTION",
            },
            "control_name": "13SIM1:cam1",
        },
        "metadata": {
            "area": "GUNB",
            "beam_path": ["SC_DIAG0", "SC_HXR", "SC_SXR"],
            "sum_l_meters": 0.0,
        },
    }
    return res


lcls_tools.common.devices.reader._device_data = _monkey_patch_device_data


def _hack_wrapper(api_method):
    """Replace when pykern.quest supports dispatch_api_call method"""

    def _wrapped(self, api_args):
        if "ui_schema" not in self:
            self._init_session()
        ux = self.ui_ctx
        rv = PKDict()
        a = api_method.__name__[_API_PREFIX_LEN:]
        if a not in _NOT_API_WITH_FIELD:
            # TODO(robnagler) The "value" is not always used.
            ux[m].value = field_value
        if (p := api_method(self, ux)) is not None:
            rv.plot = p
        # TODO(robnagler) qcall should have API name on qcall
        if m != "single_button":
            # TODO(robnagler) ui_ctx or something name? in the typescript; "model" is too general
            # TODO(robnagler) return edits; have function that updates nested attrs in py and ts
            rv.model = ux
        return rv


class ScreenAPI(slicops.quest.API):
    """Implementation for the Screen (Profile Monitor) application"""

    @_hack_wrapper
    def api_screen_beam_path(self, ux):
        # TODO(robnagler) get from device db
        ux.camera.valid_values = self.session.ui_schema.cameras_for_beam_path(
            ux.beam_path.value
        )
        if ux.camera.value in ux.camera.valid_values:
            ux.start_button.enabled = True
            ux.stop_button.enabled = False
            ux.single_button.enabled = True
        else:
            # selected camera is not in beam_path
            ux.camera.value = None
            ux.pv.value = None
            ux.start_button.enabled = False
            ux.stop_button.enabled = False
            ux.single_button.enabled = False
        # TODO(pjm): could return a diff of model changes rather than full model
        # OK to return in place values, not copy, becasue
        return None

    @_hack_wrapper
    def api_screen_camera(self, ux):
        ux.start_button.enabled = True
        ux.stop_button.enabled = False
        ux.single_button.enabled = True
        ux.pv.value = slicops.app.screen_schema.get_camera_pv(
            ux.beam_path.value,
            ux.camera.value,
        )
        return None

    @_hack_wrapper
    def api_screen_camera_gain(self, ux):
        self.session.screen_device.put_pv("Gain", ux.camera_gain.value)
        return self._return(ux)

    @_hack_wrapper
    def api_screen_color_map(self, ux):
        return None

    @_hack_wrapper
    def api_screen_curve_fit_method(self, ux):
        return self._get_image(ux, with_retry=True)

    @_hack_wrapper
    def api_screen_single_button(self, ux):
        self.session.screen_device.start()
        i = self._get_image(ux, with_retry=True)
        self.session.screen_device.stop()
        return i

    @_hack_wrapper
    def api_screen_start_button(self, ux):
        self.session.screen_device.start()
        ux.start_button.enabled = False
        ux.stop_button.enabled = True
        ux.single_button.enabled = False
        return self._get_image(ux, with_retry=True)

    @_hack_wrapper
    def api_screen_stop_button(self, ux):
        self.session.screen_device.stop()
        ux.start_button.enabled = True
        ux.stop_button.enabled = False
        ux.single_button.enabled = True
        return None

    @_hack_wrapper
    def api_screen_ui_ctx(self, api_args):
        return None

    def _fit_profile(self, profile, method):
        """Use the lcls_tools FittingTool to match the selected method.
        Valid methods are (gaussian, super_gaussian).
        """
        ft = lcls_tools.common.data.fitting_tool.FittingTool(profile)
        ft.initial_params = {
            method: ft.initial_params[method],
        }
        try:
            r = ft.get_fit()
            # TODO(pjm): FittingTool returns initial params on failure
            if r[method]["params"] == ft.initial_params[method]["params"]:
                raise RuntimeError("Fit failed")
        except RuntimeError:
            return PKDict(
                lineout=profile.tolist(),
                fit=PKDict(
                    fit_line=numpy.zeros(len(profile)).tolist(),
                    results=PKDict(
                        error="Curve fit was unsuccessful",
                    ),
                ),
            )
        g = r[method]["params"]
        return PKDict(
            lineout=profile.tolist(),
            fit=PKDict(
                fit_line=getattr(ft, method)(x=ft.x, **g).tolist(),
                results=g,
            ),
        )

    def _get_image(self, ux, with_retry=False):
        try:
            raw_pixels = self.session.screen_device.get_image()
            return PKDict(
                # TODO(pjm): output handler should support ndarray, avoiding tolist()
                raw_pixels=raw_pixels.tolist(),
                x=self._fit_profile(raw_pixels.sum(axis=0), ux.curve_fit_method.value),
                y=self._fit_profile(
                    raw_pixels.sum(axis=1)[::-1],
                    ux.curve_fit_method.value,
                ),
            )
        except ValueError as err:
            if with_retry:
                # TODO(pjm): need a retry with timeout here if first acquiring and no image is available yet
                #    sleep() needs to be replaced with async sleep?
                time.sleep(1)
                # no retry
                return self._get_image()
            raise err

    def _init_session(self):
        self.session.ui_schema = slicops.ui_schema.load(_NAME)
        self.session.ui_ctx = ux = slicops.app.screen_schema.default_ui_ctx()
        ux.beam_path.value = _cfg.dev.beam_path
        ux.camera.value = _cfg.dev.camera_name
        s = self.session.ui_schema
        ux.camera.valid_values = s.cameras_for_beam_path(_cfg.dev.beam_path)
        ux.pv.value = s.camera_pv(_cfg.dev.beam_path, _cfg.dev.camera_name)
        self.session.screen_device = _ScreenDevice(self.session.ui_schema)
        # TODO(pjm): only get this value if the selected camera supports Gain
        ux.camera_gain.value = self.session.screen_device.get_pv("Gain")
        return ux


class _ScreenDevice:
    """Screen device interaction. All EPICS access occurs at this level."""

    def __init__(self, schema):
        self.screen = lcls_tools.common.devices.reader.create_screen(
            schema.camera_area(_cfg.dev.beam_path, _cfg.dev.camera_name)
        ).screens[_cfg.dev.camera_name]

    def get_image(self):
        """Gets raw pixels from EPICS"""
        try:
            # TODO(pjm): the row/columns is reversed in lcls_tools
            #  possibly this needs to be a flag in the camera meta data
            return self.screen.image.reshape(self.screen.n_rows, self.screen.n_columns)
        except PVInvalidError as err:
            # TODO(pjm): could provide a better error message here
            raise err
        except AttributeError as err:
            # most likely EPICS PV is unavailable due to timeout,
            #  Screen.image should raise an exception if no connection is completed
            #  for now, catch AttributeError: 'NoneType' object has no attribute 'reshape'
            # TODO(pjm): could provide a better error message here
            raise err
        except ValueError as err:
            # similar to the above, connection works but image IOC is misconfigured
            # ex. cannot reshape array of size 0 into shape (1024,1024)
            raise err

    def get_pv(self, name):
        """Get a PV value by name"""
        pv = PV(self._pv_name(name))
        v = pv.get()
        if not pv.connected:
            raise PVInvalidError(f"Unable to connect to PV: {n}")
        return v

    def is_acquiring_images(self):
        """Returns True if the camera's EPICS value indicates it is capturing images."""
        try:
            return bool(self.get_pv("Acquire"))
        except PVInvalidError as err:
            # does not return an error, the initial camera may not be currently available
            return False

    def start(self):
        """Set the EPICS camera to acquire mode."""
        self.put_pv("Acquire", 1)

    def stop(self):
        """Set the EPICS camera to stop acquire mode."""
        self.put_pv("Acquire", 0)

    def put_pv(self, name, value):
        """Set a PV value."""
        pv = PV(self._pv_name(name))
        v = pv.put(value)
        if not pv.connected:
            raise PVInvalidError(f"Unable to connect to PV: {n}")
        if not v:
            raise PVInvalidError(f"Update failed for PV: {n}")

    def _pv_name(self, name):
        return f"{self.screen.controls_information.control_name}:{name}"


_cfg = pkconfig.init(
    dev=PKDict(
        beam_path=("SC_SXR", str, "dev beampath name"),
        camera_name=("DEV_CAMERA", str, "dev camera name"),
    ),
)
