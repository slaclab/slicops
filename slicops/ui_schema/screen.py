"""Screen (Profile Monitor) schema definition

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp


class _ScreenSchema(PKDict):
    def default_ui_ctx(self):
        # TODO(pjm): create field values from schema above with default values
        # TODO(robnagler): return an object
        return PKDict(
            beam_path=PKDict(
                # TODO(robnagler) Valid values should be consistent (list of lists or just dict? order matters)
                label="Beam Path",
                enabled=True,
                valid_values=(),
                value=None,
                visible=True,
            ),
            camera=PKDict(
                label="Camera",
                enabled=True,
                valid_values=(),
                value=None,
                visible=True,
            ),
            # TODO(robnagler) check gain accessor
            camera_gain=PKDict(
                label="Gain",
                enabled=True,
                value=None,
                visible=True,
            ),
            pv=PKDict(
                label="PV",
                enabled=False,
                value=None,
                visible=True,
            ),
            color_map=PKDict(
                label="Color Map",
                value="Inferno",
                valid_values=["Cividis", "Blues", "Inferno", "Turbo", "Viridis"],
                visible=True,
                enabled=True,
            ),
            curve_fit_method=PKDict(
                label="Curve Fit Method",
                value="gaussian",
                valid_values=(
                    ("gaussian", "Gaussian"),
                    ("super_gaussian", "Super Gaussian"),
                ),
                visible=True,
                enabled=True,
            ),
            single_button=PKDict(
                buttonClass="outline-info",
                enabled=True,
                label="Single",
                value=None,
                visible=True,
            ),
            start_button=PKDict(
                buttonClass="primary",
                enabled=True,
                label="Start",
                value=None,
                visible=True,
            ),
            stop_button=PKDict(
                buttonClass="danger",
                enabled=False,
                label="Stop",
                value=None,
                visible=True,
            ),
        )


SINGLETON = _ScreenSchema(
    # constants=PKDict(
    # TODO(robnagler) unused and not clear it will be used
    # color_map=["Cividis", "Cool", "Inferno", "Magma", "Plasma", "Viridis", "Warm"],
    # curve_fit_method=[
    #     ["gaussian", "Gaussian"],
    #     ["super_gaussian", "Super Gaussian"],
    # ],
    # ),
    # TODO(robnagler) unused and not clear it will be used
    # model=PKDict(
    #     screen=PKDict(
    #         beam_path=["Beam Path", "beam_path"],
    #         camera=["Camera", "camera"],
    #         camera_image=["Camera Image", "camera_image"],
    #         color_map=["Color Map", "color_map", "Inferno"],
    #         curve_fit_method=["Curve Fit Method", "curve_fit_method", "gaussian"],
    #         pv=["PV", "camera_pv"],
    #         single_button=["Single", "single_button"],
    #         start_button=["Start", "start_button"],
    #         stop_button=["Stop", "stop_button"],
    #     ),
    # ),
    # view=PKDict(
    #     screen=PKDict(
    #         fields=[
    #             [
    #                 "beam_path",
    #                 "camera",
    #                 "pv",
    #                 "start_button",
    #                 "stop_button",
    #                 "single_button",
    #             ],
    #             [
    #                 "camera_image",
    #                 "curve_fit_method",
    #                 "color_map",
    #             ],
    #         ],
    #     ),
    # ),
)
