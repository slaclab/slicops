"""Screen (Profile Monitor) implementation

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from lcls_tools.common.controls.pyepics.utils import PV, PVInvalidError
from lcls_tools.common.devices.reader import create_screen
from pykern import pkconfig
from pykern import pkresource
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import lcls_tools.common.data.fitting_tool
import math
import numpy
import random

_cfg = None


def new_implementation(args):
    return Screen(**args)


class Screen(PKDict):
    """Implementation for the Screen (Profile Monitor) application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def action_start_button(self):
        return ScreenDevice().start()

    def action_stop_button(self):
        return ScreenDevice().stop()

    def action_get_image(self):
        raw_pixels = ScreenDevice().get_image()
        x = raw_pixels.sum(axis=0)
        y = raw_pixels.sum(axis=1)
        yfit = self._fit(y[::-1], self.api_args.curve_fit)
        xfit = self._fit(x, self.api_args.curve_fit)
        return PKDict(
            # TODO(pjm): output handler should support ndarray, avoiding tolist()
            raw_pixels=raw_pixels.tolist(),
            x_lineout=x.tolist(),
            y_lineout=y[::-1].tolist(),
            # x_fit=xfit.tolist(),
            # y_fit=yfit[::-1].tolist(),
            x_fit=xfit,
            y_fit=yfit,
        )

    def action_is_acquiring_images(self):
        return ScreenDevice().is_acquiring_images()

    def default_instance(self):
        # TODO(pjm): dummy data
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
            ),
        )

    def schema(self):
        # TODO(pjm): schema could be pulled from a file
        return PKDict(
            constants=PKDict(
                BeamPath=[
                    # TODO(pjm): dummy data, should be generated from yaml or csv sources
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
    """Screen device interaction. All EPICS access occurs at this level.
    Includes a dummy camera implementation if EPICS access is not enabled.
    """

    def __init__(self):
        self.screen = None
        if _cfg.dev.use_epics:
            self.screen = create_screen(_cfg.dev.beam_path).screens[
                _cfg.dev.camera_name
            ]

    def get_image(self):
        """Gets raw pixels from EPICS or from the configured dummmy camera."""
        raw_pixels = None
        if self.screen:
            try:
                return self.screen.image
            except PVInvalidError as err:
                # TODO(pjm): could provide a better error message here
                raise err
            except AttributeError as err:
                # most likely EPICS PV is unavailable due to timeout,
                #  Screen.image should raise an exception if no connection is completed
                #  for now, catch AttributeError: 'NoneType' object has no attribute 'reshape'
                # TODO(pjm): could provide a better error message here
                raise err
        return numpy.fromfile(
            pkresource.file_path(
                _cfg.dev.dummy_camera.template.format(
                    math.floor(random.random() * _cfg.dev.dummy_camera.count + 1),
                    1,
                )
            ),
            dtype=(
                numpy.uint8 if _cfg.dev.dummy_camera.dtype == "uint8" else numpy.uint16
            ),
        ).reshape(
            _cfg.dev.dummy_camera.dimensions,
        )

    def is_acquiring_images(self):
        """Returns True if the camera's EPICS value indicates it is capturing images."""
        if self.screen:
            try:
                return PKDict(is_acquiring_images=bool(self._acquire_pv()[0].get()))
            except PVInvalidError as err:
                # does not return an error, the initial camera may not be available
                return PKDict(is_acquiring_images=False)
        return PKDict(is_acquiring_images=True)

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
        if self.screen:
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
        dummy_camera=dict(
            template=("screen/image-640x480-8bit-{:02d}.bin", str, "image filename"),
            count=(12, int, "number of image files"),
            dtype=("uint8", str, "image data type"),
            dimensions=((480, 640), tuple, "image dimensions"),
            # template=("screen/image2-1292x964-16bit-{:02d}.bin", str, "image filename"),
            # count=(1, int, "number of image files"),
            # dtype=("uint16", str, "image data type"),
            # dimensions=((964, 1292), tuple, "image dimensions"),
        ),
        beam_path=("VCC", str, "dev beampath name"),
        camera_name=("PJMDEV", str, "dev camera name"),
        use_epics=(False, bool, "Enable EPICS access"),
    ),
)
