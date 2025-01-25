"""Screen (Profile Monitor) UI API

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern import pkconfig
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import asyncio
import lcls_tools.common.data.fitting_tool
import numpy
import random
import slicops.device
import slicops.quest
import slicops.ui_schema
import time

_NAME = "screen"

_cfg = None


class API(slicops.quest.API):
    """Implementation for the Screen (Profile Monitor) application"""

    async def api_screen_beam_path(self, api_args):
        ux = self._save_field("beam_path", api_args)
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
        return self._return(ux)

    async def api_screen_camera(self, api_args):
        ux = self._save_field("camera", api_args)
        ux.start_button.enabled = True
        ux.stop_button.enabled = False
        ux.single_button.enabled = True
        ux.pv.value = self.session.ui_schema.get_camera_pv(
            ux.beam_path.value,
            ux.camera.value,
        )
        return self._return(ux)

    async def api_screen_camera_gain(self, api_args):
        ux = self._save_field("camera_gain", api_args)
        self.session.device.put("gain", ux.camera_gain.value)
        return self._return(ux)

    async def api_screen_color_map(self, api_args):
        ux = self._args("color_map", api_args)
        return self._return(ux)

    async def api_screen_curve_fit_method(self, api_args):
        ux = self._args("curve_fit_method", api_args)
        return await self._return_with_image(ux)

    async def api_screen_single_button(self, api_args):
        ux = self._session_ui_ctx()
        self._set_acquire(1)
        try:
            return await self._return_with_image(ux)
        finally:
            # TODO(robnagler) if raised, then ignore errors here. First error is returned
            self._set_acquire(0)

    async def api_screen_start_button(self, api_args):
        ux = self._session_ui_ctx()
        self._set_acquire(1)
        ux.start_button.enabled = False
        ux.stop_button.enabled = True
        ux.single_button.enabled = False
        return await self._return_with_image(ux)

    async def api_screen_stop_button(self, api_args):
        ux = self._session_ui_ctx()
        self._set_acquire(0)
        ux.start_button.enabled = True
        ux.stop_button.enabled = False
        ux.single_button.enabled = True
        return self._return(ux)

    async def api_screen_ui_ctx(self, api_args):
        ux = self._session_ui_ctx()
        return self._return(ux)

    def _is_acquiring(self):
        try:
            return self.session.device.get("acquire")
        except slicops.device.DeviceError as err:
            # does not return an error, the initial camera may not be currently available
            return False

    def _return(self, ux):
        return PKDict(ui_ctx=ux)

    async def _return_with_image(self, ux):
        def _fit(profile):
            """Use the lcls_tools FittingTool to match the selected method.
            Valid methods are (gaussian, super_gaussian).
            """
            t = lcls_tools.common.data.fitting_tool.FittingTool(profile)
            m = ux.curve_fit_method.value
            return _fit_do(profile, t, m, t.initial_params[m])

        def _fit_do(profile, tool, method, initial_params):
            # TODO(robnagler) why is this done?
            tool.initial_params = PKDict({method: initial_params})
            try:
                p = tool.get_fit()[method]["params"]
                # TODO(pjm): FittingTool returns initial params on failure
                if p == initial_params:
                    return _fit_error(profile)
            except RuntimeError:
                # TODO(robnagler) does this happen?
                return _fit_error(profile)
            return PKDict(
                lineout=profile.tolist(),
                fit=PKDict(
                    fit_line=getattr(tool, method)(x=tool.x, **p).tolist(),
                    results=p,
                ),
            )

        def _fit_error(profile):
            return PKDict(
                lineout=profile.tolist(),
                fit=PKDict(
                    fit_line=numpy.zeros(len(profile)).tolist(),
                    results=PKDict(
                        error="Curve fit was unsuccessful",
                    ),
                ),
            )

        async def _profile():
            for i in range(2):
                try:
                    return self.session.device.get("image")
                except (ValueError, slicops.device.DeviceError) as err:
                    if i >= 1:
                        raise err
                await asyncio.sleep(1)
            raise AssertionError("should not get here")

        p = await _profile()
        return self._return(ux).pkupdate(
            plot=PKDict(
                # TODO(pjm): output handler should support ndarray, avoiding tolist()
                raw_pixels=p.tolist(),
                x=_fit(p.sum(axis=0)),
                y=_fit(p.sum(axis=1)[::-1]),
            ),
        )

    def _save_field(self, field_name, api_args):
        ux = self._session_ui_ctx()
        ux[field_name].value = api_args.field_value
        return ux

    def _session_ui_ctx(self):
        if ux := self.session.get("ui_ctx"):
            return ux
        self.session.ui_schema = slicops.ui_schema.load(_NAME)
        self.session.ui_ctx = ux = self.session.ui_schema.default_ui_ctx()
        ux.beam_path.value = _cfg.dev.beam_path
        ux.camera.value = _cfg.dev.camera_name
        s = self.session.ui_schema
        ux.camera.valid_values = s.cameras_for_beam_path(_cfg.dev.beam_path)
        ux.pv.value = s.camera_pv(_cfg.dev.beam_path, _cfg.dev.camera_name)
        self.session.device = slicops.device.Device(_cfg.dev.camera_name)
        # TODO(pjm): only get this value if the selected camera supports gain
        ux.camera_gain.value = self.session.device.get("gain")
        # TODO(robnagler) is_acquiring set button state
        return ux

    def _set_acquire(self, is_on):
        self.session.device.put("acquire", is_on)


_cfg = pkconfig.init(
    dev=PKDict(
        beam_path=("SC_SXR", str, "dev beampath name"),
        camera_name=("DEV_CAMERA", str, "dev camera name"),
    ),
)
