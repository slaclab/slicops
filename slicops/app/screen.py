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
import slicops.app.screen_schema
import time

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


def new_implementation(args):
    return Screen(**args)


class Screen(PKDict):
    """Implementation for the Screen (Profile Monitor) application"""

    # TODO(pjm): the session state, needs to be tied to an id
    _session_state = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def action_beam_path(self, value):
        m = self.session_state().model
        m.beam_path.value = value
        m.camera.valid_values = slicops.app.screen_schema.get_cameras_for_beam_path(
            value
        )
        if m.camera.value in m.camera.valid_values:
            m.start_button.enabled = True
            m.stop_button.enabled = False
            m.single_button.enabled = True
        else:
            # selected camera is not in beam_path
            m.camera.value = None
            m.pv.value = None
            m.start_button.enabled = False
            m.stop_button.enabled = False
            m.single_button.enabled = False
        # TODO(pjm): could return a diff of model changes rather than full model
        return PKDict(
            model=m,
        )

    def action_camera(self, value):
        m = self.session_state().model
        m.camera.value = value
        m.start_button.enabled = True
        m.stop_button.enabled = False
        m.single_button.enabled = True
        m.pv.value = slicops.app.screen_schema.get_camera_pv(
            m.beam_path.value,
            m.camera.value,
        )
        return PKDict(
            model=m,
        )

    def action_camera_gain(self, value):
        m = self.session_state().model
        m.camera_gain.value = value
        ScreenDevice().put_pv("Gain", value)
        return PKDict(
            model=m,
        )

    def action_color_map(self, value):
        m = self.session_state().model
        m.color_map.value = value
        return PKDict(
            model=m,
        )

    def action_curve_fit_method(self, value):
        m = self.session_state().model
        m.curve_fit_method.value = value
        return PKDict(
            model=m,
            plot=self._get_image(with_retry=True),
        )

    def action_single_button(self, value):
        ScreenDevice().start()
        i = self._get_image(with_retry=True)
        ScreenDevice().stop()
        return PKDict(
            plot=i,
        )

    def action_start_button(self, value):
        m = self.session_state().model
        ScreenDevice().start()
        m.start_button.enabled = False
        m.stop_button.enabled = True
        m.single_button.enabled = False
        return PKDict(
            model=m,
            plot=self._get_image(with_retry=True),
        )

    def action_stop_button(self, value):
        m = self.session_state().model
        ScreenDevice().stop()
        m.start_button.enabled = True
        m.stop_button.enabled = False
        m.single_button.enabled = True
        return PKDict(model=m)

    def session_state(self):
        # TODO(pjm): need data store, using a class var for now
        if Screen._session_state is None:
            Screen._session_state = PKDict(
                model=self._default_model(),
            )
        return Screen._session_state

    def _default_model(self):
        m = slicops.app.screen_schema.new_model()
        m.beam_path.value = _cfg.dev.beam_path
        m.camera.value = _cfg.dev.camera_name
        m.camera.valid_values = slicops.app.screen_schema.get_cameras_for_beam_path(
            _cfg.dev.beam_path
        )
        m.pv.value = slicops.app.screen_schema.get_camera_pv(
            _cfg.dev.beam_path, _cfg.dev.camera_name
        )
        # TODO(pjm): only get this value if the selected camera supports Gain
        m.camera_gain.value = ScreenDevice().get_pv("Gain")
        return m

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

    def _get_image(self, with_retry=False):
        m = self.session_state().model
        try:
            raw_pixels = ScreenDevice().get_image()
            return PKDict(
                # TODO(pjm): output handler should support ndarray, avoiding tolist()
                raw_pixels=raw_pixels.tolist(),
                x=self._fit_profile(raw_pixels.sum(axis=0), m.curve_fit_method.value),
                y=self._fit_profile(
                    raw_pixels.sum(axis=1)[::-1],
                    m.curve_fit_method.value,
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


class ScreenDevice:
    """Screen device interaction. All EPICS access occurs at this level."""

    def __init__(self):
        self.screen = lcls_tools.common.devices.reader.create_screen(
            slicops.app.screen_schema.get_camera_area(
                _cfg.dev.beam_path, _cfg.dev.camera_name
            ),
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
