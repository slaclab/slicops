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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def action_camera_gain(self):
        # TODO(pjm): need PV config for gain
        return ScreenDevice().put_pv("Gain", self.api_args.camera_gain)

    def action_get_image(self):
        """Returns an image and x/y profiles with computed fitting"""
        raw_pixels = ScreenDevice().get_image()
        return PKDict(
            image=PKDict(
                # TODO(pjm): output handler should support ndarray, avoiding tolist()
                raw_pixels=raw_pixels.tolist(),
                x=self._fit_profile(raw_pixels.sum(axis=0), self.api_args.curve_fit),
                y=self._fit_profile(
                    raw_pixels.sum(axis=1)[::-1], self.api_args.curve_fit
                ),
            ),
        )

    def action_start_button(self):
        """Starts image acquisition and returns an image"""
        ScreenDevice().start()
        # TODO(pjm): need a retry with timeout here if first acquiring and no image is available yet
        return self.action_get_image()

    def action_single_button(self):
        """Acquires a single image and then stops acquisition"""
        res = self.action_start_button()
        ScreenDevice().stop()
        return res

    def action_stop_button(self):
        ScreenDevice().stop()
        return PKDict()

    def default_model(self):
        # TODO(pjm): need data store
        s = ScreenDevice()
        return PKDict(
            screen=PKDict(
                beam_path=_cfg.dev.beam_path,
                camera=_cfg.dev.camera_name,
                pv=slicops.app.screen_schema.get_camera_pv(
                    _cfg.dev.beam_path, _cfg.dev.camera_name
                ),
                curve_fit_method="gaussian",
                color_map="Inferno",
                camera_image=None,
                acquire_button=None,
                stop_button=None,
                single_button=None,
                # TODO(pjm): don't use get_pv_or_default()  - takes too long on failure and would be multiple times
                camera_gain=s.get_pv_or_default("Gain", 180),
                # TODO(pjm): this is a potentially very slow operation if the default camera is unavailable
                is_acquiring_images=s.is_acquiring_images(),
            ),
        )

    def schema(self):
        return slicops.app.screen_schema.SCHEMA

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

    def get_pv_or_default(self, name, default_value):
        """Get a PV value by name or return a default value if not available"""
        try:
            return self.get_pv(name)
        except PVInvalidError:
            return default_value

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
