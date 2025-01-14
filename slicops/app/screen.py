"""Screen (Profile Monitor) implementation

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from lcls_tools.common.controls.pyepics.utils import PV, PVInvalidError
from pykern import pkconfig
from pykern import pkresource
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import lcls_tools.common.data.fitting_tool
import lcls_tools.common.devices.reader
import math
import numpy
import random

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

    def action_start_button(self):
        """Starts image acquisition and returns an image"""
        ScreenDevice().start()
        return self.action_get_image()

    def action_single_button(self):
        """Acquires a single image and then stops acquisition"""
        res = self.action_start_button()
        ScreenDevice().stop()
        return res

    def action_stop_button(self):
        return ScreenDevice().stop()

    def action_get_image(self):
        raw_pixels = ScreenDevice().get_image()
        x = raw_pixels.sum(axis=0)
        y = raw_pixels.sum(axis=1)
        # TODO(pjm): return structure x and y with values, compute in loop
        yfit = self._fit(y[::-1], self.api_args.curve_fit)
        xfit = self._fit(x, self.api_args.curve_fit)
        return PKDict(
            image=PKDict(
                # TODO(pjm): output handler should support ndarray, avoiding tolist()
                raw_pixels=raw_pixels.tolist(),
                x_lineout=x.tolist(),
                y_lineout=y[::-1].tolist(),
                x_fit=xfit,
                y_fit=yfit,
            ),
        )

    def default_model(self):
        # TODO(pjm): need data store
        return PKDict(
            screen=PKDict(
                beam_path="SC_HXR",
                camera="VCCB",
                pv="CAMR:LGUN:950",
                curve_fit_method="gaussian",
                camera_image=None,
                acquire_button=None,
                stop_button=None,
                single_button=None,
                # TODO(pjm): this is a potentially very slow operation if the default camera is unavailable
                is_acquiring_images=ScreenDevice().is_acquiring_images(),
            ),
        )

    def schema(self):
        # TODO(pjm): schema could be pulled from a file
        return PKDict(
            constants=PKDict(
                BeamPath=[
                    # TODO(pjm): should be generated from yaml or csv sources
                    PKDict(
                        name="CU_HXR",
                        screens=[
                            ["OTR11", "OTRS:LI21:237"],
                            ["OTR12", "OTRS:LI21:291"],
                            ["OTR2", "OTRS:IN20:571"],
                            ["OTR21", "OTRS:LI24:807"],
                            ["OTR3", "OTRS:IN20:621"],
                            ["OTR30", "OTRS:LTU1:449"],
                            ["OTR33", "OTRS:LTUH:745"],
                            ["OTR4", "OTRS:IN20:711"],
                            ["OTRDMP", "OTRS:DMPH:695"],
                            ["OTRH1", "OTRS:IN20:465"],
                            ["OTRH2", "OTRS:IN20:471"],
                            ["VCC", "CAMR:IN20:186"],
                            ["YAG01", "YAGS:IN20:211"],
                            ["YAG02", "YAGS:IN20:241"],
                            ["YAG03", "YAGS:IN20:351"],
                            ["YAGPSI", "YAGS:LTUH:743"],
                        ],
                    ),
                    PKDict(
                        name="SC_HXR",
                        screens=[
                            ["OTR11B", "PROF:BC1B:470"],
                            ["OTR21B", "PROF:BC2B:545"],
                            ["OTRC006", "PROF:COL0:535"],
                            ["OTRDMP", "OTRS:DMPH:695"],
                            ["OTRDOG", "PROF:DOG:195"],
                            ["VCCB", "CAMR:LGUN:950"],
                            ["YAGH1", "YAGS:HTR:625"],
                            ["YAGH2", "YAGS:HTR:675"],
                            ["YAGPSI", "YAGS:LTUH:743"],
                        ],
                    ),
                ],
                ColorMap=["Inferno", "Viridis"],
                CurveFitMethod=[
                    ["gaussian", "Gaussian"],
                    ["super_gaussian", "Super Gaussian"],
                    ["double_gaussian", "Double Gaussian"],
                ],
            ),
            model=PKDict(
                screen=PKDict(
                    beam_path=["Beam Path", "BeamPath"],
                    camera=["Camera", "Camera"],
                    pv=["PV", "CameraPV"],
                    curve_fit_method=["Curve Fit Method", "CurveFitMethod", "gaussian"],
                    color_map=["Color Map", "ColorMap", "Inferno"],
                    camera_image=["Camera Image", "CameraImage"],
                    start_button=["Start", "StartButton"],
                    stop_button=["Stop", "StopButton"],
                    single_button=["Single", "SinglButton"],
                ),
            ),
            view=PKDict(
                screen=PKDict(
                    fields=[
                        [
                            "beam_path",
                            "camera",
                            "pv",
                            "start_button",
                            "stop_button",
                            "single_button",
                        ],
                        [
                            "camera_image",
                            "curve_fit_method",
                            "color_map",
                        ],
                    ],
                ),
            ),
        )

    def _fit(self, line, method):
        """Use the lcls_tools FittingTool to match the selected method.
        Valid methods are (gaussian, super_gaussian, double_gaussian).
        """
        ft = lcls_tools.common.data.fitting_tool.FittingTool(line)
        # TODO(pjm): need to pass hints to guesser (mu, nu), translated from domain units to pixels
        if method == "double_gaussian":
            ft.initial_params["double_gaussian"]["params"]["mu"] = 473
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
                fit_line=numpy.zeros(len(line)).tolist(),
                results=PKDict(
                    error="Curve fit was unsuccessful",
                ),
            )
        g = r[method]["params"]
        return PKDict(
            fit_line=getattr(ft, method)(x=ft.x, **g).tolist(),
            results=g,
        )


class ScreenDevice:
    """Screen device interaction. All EPICS access occurs at this level."""

    def __init__(self):
        self.screen = lcls_tools.common.devices.reader.create_screen(
            _cfg.dev.beam_path
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

    def is_acquiring_images(self):
        """Returns True if the camera's EPICS value indicates it is capturing images."""
        try:
            return bool(self._acquire_pv()[0].get())
        except PVInvalidError as err:
            # does not return an error, the initial camera may not be currently available
            return False

    def start(self):
        """Set the EPICS camera to acquire mode."""
        self._set_acquire(1)

    def stop(self):
        """Set the EPICS camera to stop acquire mode."""
        return self._set_acquire(0)

    def _acquire_pv(self):
        n = f"{self.screen.controls_information.control_name}:Acquire"
        return (PV(n), n)

    def _set_acquire(self, is_on):
        try:
            pv, n = self._acquire_pv()
            pv.put(is_on)
            if not pv.connected:
                raise PVInvalidError(f"Unable to connect to PV: {n}")
        except PVInvalidError as err:
            # TODO(pjm): could provide a better error message here
            raise err
        return PKDict()


_cfg = pkconfig.init(
    dev=PKDict(
        beam_path=("VCC", str, "dev beampath name"),
        camera_name=("DEV_CAMERA", str, "dev camera name"),
    ),
)
