"""Screen (Profile Monitor) schema definition

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict

# TODO(pjm): should be immutable
SCHEMA = PKDict(
    constants=PKDict(
        BeamPath=PKDict(
            # beam path -> camera name -> [camera pv, area]
            CU_ALINE=PKDict(
                YAG01=["YAGS:IN20:211", "GUN"],
                YAG02=["YAGS:IN20:241", "L0"],
                YAG03=["YAGS:IN20:351", "L0"],
                OTR11=["OTRS:LI21:237", "BC1"],
                OTR12=["OTRS:LI21:291", "BC1"],
                OTR21=["OTRS:LI24:807", "BC2"],
            ),
            CU_HXR=PKDict(
                VCC=["CAMR:IN20:186", "VCC"],
                YAG01=["YAGS:IN20:211", "GUN"],
                YAG02=["YAGS:IN20:241", "L0"],
                YAG03=["YAGS:IN20:351", "L0"],
                OTR11=["OTRS:LI21:237", "BC1"],
                OTR12=["OTRS:LI21:291", "BC1"],
                OTR21=["OTRS:LI24:807", "BC2"],
                OTRDMP=["OTRS:DMPH:695", "DMPH"],
            ),
            CU_SXR=PKDict(
                VCC=["CAMR:IN20:186", "VCC"],
                YAG01=["YAGS:IN20:211", "GUN"],
                YAG02=["YAGS:IN20:241", "L0"],
                YAG03=["YAGS:IN20:351", "L0"],
                OTR11=["OTRS:LI21:237", "BC1"],
                OTR12=["OTRS:LI21:291", "BC1"],
                OTR21=["OTRS:LI24:807", "BC2"],
                BOD10=["YAGS:UNDS:3575", "UNDS"],
                BOD12=["YAGS:UNDS:3795", "UNDS"],
                OTRDMPB=["OTRS:DMPS:695", "DMPS"],
            ),
            SC_BSYD=PKDict(
                OTR0H04=["OTRS:HTR:330", "HTR"],
                YAGH1=["YAGS:HTR:625", "HTR"],
                YAGH2=["YAGS:HTR:675", "HTR"],
                OTRC006=["PROF:COL0:535", "COL0"],
                OTR11B=["PROF:BC1B:470", "BC1B"],
                OTR21B=["PROF:BC2B:545", "BC2B"],
                OTRDOG=["PROF:DOG:195", "DOG"],
            ),
            SC_DASEL=PKDict(
                OTR0H04=["OTRS:HTR:330", "HTR"],
                YAGH1=["YAGS:HTR:625", "HTR"],
                YAGH2=["YAGS:HTR:675", "HTR"],
                OTRC006=["PROF:COL0:535", "COL0"],
                OTR11B=["PROF:BC1B:470", "BC1B"],
                OTR21B=["PROF:BC2B:545", "BC2B"],
                OTRDOG=["PROF:DOG:195", "DOG"],
                PRDAS12=["PROF:DASEL:440", "DASEL"],
                PRDAS14=["PROF:DASEL:655", "DASEL"],
                PRDAS17=["PROF:DASEL:818", "DASEL"],
            ),
            SC_DIAG0=PKDict(
                DEV_CAMERA=["13SIM1:cam1", "VCC"],
                VCCB=["CAMR:LGUN:950", "VCC"],
                OTR0H04=["OTRS:HTR:330", "HTR"],
                YAGH1=["YAGS:HTR:625", "HTR"],
                YAGH2=["YAGS:HTR:675", "HTR"],
                OTRDG02=["OTRS:DIAG0:420", "DIAG0"],
                OTRDG04=["OTRS:DIAG0:525", "DIAG0"],
            ),
            SC_HXR=PKDict(
                DEV_CAMERA=["13SIM1:cam1", "VCC"],
                VCCB=["CAMR:LGUN:950", "VCC"],
                OTR0H04=["OTRS:HTR:330", "HTR"],
                YAGH1=["YAGS:HTR:625", "HTR"],
                YAGH2=["YAGS:HTR:675", "HTR"],
                OTRC006=["PROF:COL0:535", "COL0"],
                OTR11B=["PROF:BC1B:470", "BC1B"],
                OTR21B=["PROF:BC2B:545", "BC2B"],
                OTRDOG=["PROF:DOG:195", "DOG"],
                OTRDMP=["OTRS:DMPH:695", "DMPH"],
            ),
            SC_SXR=PKDict(
                DEV_CAMERA=["13SIM1:cam1", "VCC"],
                VCCB=["CAMR:LGUN:950", "VCC"],
                OTR0H04=["OTRS:HTR:330", "HTR"],
                YAGH1=["YAGS:HTR:625", "HTR"],
                YAGH2=["YAGS:HTR:675", "HTR"],
                OTRC006=["PROF:COL0:535", "COL0"],
                OTR11B=["PROF:BC1B:470", "BC1B"],
                OTR21B=["PROF:BC2B:545", "BC2B"],
                OTRDOG=["PROF:DOG:195", "DOG"],
                BOD10=["YAGS:UNDS:3575", "UNDS"],
                BOD12=["YAGS:UNDS:3795", "UNDS"],
                OTRDMPB=["OTRS:DMPS:695", "DMPS"],
            ),
        ),
        ColorMap=["Cividis", "Cool", "Inferno", "Magma", "Plasma", "Viridis", "Warm"],
        CurveFitMethod=[
            ["gaussian", "Gaussian"],
            ["super_gaussian", "Super Gaussian"],
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
            single_button=["Single", "SingleButton"],
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


def get_camera_area(beam_path, camera_name):
    return SCHEMA.constants.BeamPath[beam_path][camera_name][1]


def get_camera_pv(beam_path, camera_name):
    return SCHEMA.constants.BeamPath[beam_path][camera_name][0]
