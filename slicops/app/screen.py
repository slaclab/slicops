"""Screen (Profile Monitor) implementation

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern import pkconfig
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import lcls_tools.common.data.fitting_tool
import slicops.device
import numpy
import random
import slicops.app.screen_schema

_cfg = None


def new_implementation(args):
    return Screen(**args)


class Screen(PKDict):
    """Implementation for the Screen (Profile Monitor) application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        return ScreenDevice().stop()

    def default_model(self):
        # TODO(pjm): need data store
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
                # TODO(pjm): this is a potentially very slow operation if the default camera is unavailable
                is_acquiring_images=ScreenDevice().is_acquiring_images(),
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
                fit_line=numpy.zeros(len(profile)).tolist(),
                results=PKDict(
                    error="Curve fit was unsuccessful",
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
        self.screen = slicops.device.Device(_cfg.dev.camera_name)

    def get_image(self):
        """Gets raw pixels from EPICS"""
        if (rv := self.screen.get("image")) is None:
            return ValueError("no image")
        if not (
            (r := self.screen.get("num_rows")) and (c := self.screen.get("num_cols"))
        ):
            raise ValueError("num_rows or num_cols is invalid")
        return rv.reshape(c, r)

    def is_acquiring_images(self):
        """Returns True if the camera's EPICS value indicates it is capturing images."""
        try:
            return self.screen.get("acquire")
        except slicops.device.DeviceError as err:
            # does not return an error, the initial camera may not be currently available
            return False

    def start(self):
        """Set the EPICS camera to acquire mode."""
        self._set_acquire(1)

    def stop(self):
        """Set the EPICS camera to stop acquire mode."""
        return self._set_acquire(0)

    def _set_acquire(self, is_on):
        self.screen.put("acquire", is_on)
        return PKDict()


_cfg = pkconfig.init(
    dev=PKDict(
        beam_path=("SC_SXR", str, "dev beampath name"),
        camera_name=("DEV_CAMERA", str, "dev camera name"),
    ),
)
