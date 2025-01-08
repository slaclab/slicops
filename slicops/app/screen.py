"""Screen (Profile Monitor) implementation

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from lcls_tools.common.controls.pyepics.utils import PV, PVInvalidError
from pykern import pkconfig
from pykern import pkresource
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
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

    def action(self):
        # TODO(pjm): get selected camera from screen model
        if self.api_args.method == "acquire_button":
            if _cfg.dev.use_epics:
                try:
                    # TODO(pjm): use camera yaml definitions
                    PV(f"{_cfg.dev.camera_pv}:Acquire").put(
                        1 if self.api_args.is_start else 0
                    )
                except PVInvalidError as err:
                    raise err
            return PKDict()
        elif self.api_args.method == "get_image":
            if _cfg.dev.use_epics:
                try:
                    return PKDict(
                        raw_pixels=PV(f"{_cfg.dev.image_pv}:ArrayData")
                        .get()
                        .reshape(
                            (
                                PV(f"{_cfg.dev.image_pv}:ArraySize1_RBV").get(),
                                PV(f"{_cfg.dev.image_pv}:ArraySize0_RBV").get(),
                            )
                        )
                        .tolist(),
                    )
                except PVInvalidError as err:
                    raise err
            else:
                # TODO(pjm): get shape and bitdepth from filename
                num = math.floor(random.random() * 10 + 1)
                return PKDict(
                    raw_pixels=numpy.fromfile(
                        pkresource.file_path(
                            f"screen/image-640x480-8bit-{num:02d}.bin"
                        ),
                        dtype=numpy.uint8,
                    )
                    .reshape((480, 640))
                    .tolist()
                )
        raise AssertionError(f"unknown action method: {self.api_args.method}")

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
                    ["assymetric", "Assymetric"],
                    ["rms_raw", "RMS raw"],
                    ["rms_cut_peak", "RMS cut peak"],
                    ["rms_cut_area", "RMS cut area"],
                    ["rms_floor", "RMS floor"],
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
                    acquire_button=["Start", "AcquireButton"],
                    stop_button=["Stop", "StopButton"],
                ),
            ),
            view=PKDict(
                screen=PKDict(
                    fields=[
                        [
                            "beam_path",
                            "camera",
                            "pv",
                            "acquire_button",
                            "stop_button",
                            "curve_fit_method",
                        ],
                        [
                            "camera_image",
                            "color_map",
                        ],
                    ],
                ),
            ),
        )


_cfg = pkconfig.init(
    dev=PKDict(
        camera_filename=(
            "image-640x480-8bit-01.bin",
            str,
            "use a static file for camera data",
        ),
        camera_pv=("13SIM1:cam1", str, "EPICS camera PV prefix for dev testing"),
        image_pv=("13SIM1:image1", str, "EPICS image PV prefix for dev testing"),
        use_epics=(False, bool, "Enable EPICS access"),
    ),
)
