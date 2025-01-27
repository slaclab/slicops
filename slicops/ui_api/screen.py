"""Screen (Profile Monitor) UI API

`API` stores ``ui_ctx`` (UI Context, local var ``ux``) in the
`pykern.http.Session`. The ``ui_ctx`` is a mirror of all state in the
client. Calls to this `API` changes the ``ui_ctx`` and possibly
invokes changes to the underlying device, also stored in the
`Session`.

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern import pkconfig
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import asyncio
import lcls_tools.common.data.fitting_tool
import numpy
import random
import slicops.device
import slicops.device_db
import slicops.quest
import slicops.ui_schema
import time

_KIND = "screen"

_cfg = None


class InvalidFieldChange(RuntimeError):

    pass


class API(slicops.quest.API):
    """Implementation for the Screen (Profile Monitor) application"""

    async def api_screen_beam_path(self, api_args):
        """Set the ``beam_path``"""
        ux, o = self._save_field("beam_path", api_args)
        if o:
            self._beam_path_change(ux, o)
        # TODO(pjm): could return a diff of model changes rather than full model
        # OK to return in place values, not copy, becasue
        return self._return(ux)

    async def api_screen_camera(self, api_args):
        """Set the ``camera`` which may change the ``device``"""
        ux, o = self._save_field("camera", api_args)
        if o:
            self._device_change(ux, o)
        return self._return(ux)

    async def api_screen_camera_gain(self, api_args):
        ux, _ = self._save_field("camera_gain", api_args)
        self.session.device.put("gain", ux.camera_gain.value)
        return self._return(ux)

    async def api_screen_color_map(self, api_args):
        ux, _ = self._save_field("color_map", api_args)
        return self._return(ux)

    async def api_screen_curve_fit_method(self, api_args):
        ux, _ = self._save_field("curve_fit_method", api_args)
        return await self._return_with_image(ux)

    async def api_screen_single_button(self, api_args):
        ux = self._session_ui_ctx()
        # TODO(robnagler) buttons should always change and be sent back,
        # because image acquisition could take time.
        self._set_acquire(1)
        try:
            return await self._return_with_image(ux)
        finally:
            # TODO(robnagler) if raised, then ignore errors here. First error is returned
            self._set_acquire(0)

    async def api_screen_start_button(self, api_args):
        ux = self._session_ui_ctx()
        self._set_acquire(1)
        self._button_setup(ux, True)
        return await self._return_with_image(ux)

    async def api_screen_stop_button(self, api_args):
        ux = self._session_ui_ctx()
        self._set_acquire(0)
        self._button_setup(ux, False)
        return self._return(ux)

    async def api_screen_ui_ctx(self, api_args):
        ux = self._session_ui_ctx()
        return self._return(ux)

    def _beam_path_change(self, ux, old_name):
        # TODO(robnagler) get from device db
        ux.camera.valid_values = slicops.device_db.devices_for_beam_path(
            ux.beam_path.value, _KIND
        )
        if ux.camera.value in ux.camera.valid_values or (o := ux.camera.value) is None:
            return
        ux.camera.value = None
        self._device_change(ux, o)

    def _button_setup(self, ux, is_acquiring):
        if is_acquiring:
            ux.single_button.enabled = False
            ux.start_button.enabled = False
            ux.stop_button.enabled = True
        else:
            ux.single_button.enabled = True
            ux.start_button.enabled = True
            ux.stop_button.enabled = False

    def _device_change(self, ux, old_name):
        def _acquiring(device):
            try:
                return device.get("acquire")
            except slicops.device.DeviceError as err:
                # does not return an error, the initial camera may not be currently available
                return False

        def _clear():
            ux.camera_gain.value = None
            ux.pv.value = None
            self._button_setup(False)

        def _destroy():
            if not old_name or not (d := self.session.get("device")):
                return
            self.session.device = None
            try:
                self._set_acquire(0)
            except Exception as e:
                pkdlog(
                    "set acquire=0 PV error={} device={} stack={}", e, d.name, pkdexc()
                )
            d.destroy()

        def _setup():
            d = self.session.device = slicops.device.Device(ux.camera.value)
            ux.camera_gain.value = ux.camera_gain.value = d.get("gain")
            ux.pv.value = d.meta.pv_prefix
            self._button_setup(ux, _acquiring(d))

        _destroy()
        if ux.camera.value is None:
            _clear()
            return
        _setup()

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
                if p == initial_params["params"]:
                    return _fit_error(profile)
            except RuntimeError:
                # TODO(robnagler) does this happen?
                return _fit_error(profile)
            return PKDict(
                lineout=profile.tolist(),
                fit=PKDict(
                    fit_line=getattr(tool, method)(x=tool.x, **p).tolist(),
                    results=p.tolist(),
                ),
            )

        def _fit_error(profile):
            # TODO(robnagler) why doesn't display the error somewhere?
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
        n = api_args.field_value
        f = ux[field_name]
        if (o := f.value) == n:
            return ux, None
        if "valid_values" in f and n not in f.valid_values:
            raise InvalidFieldChange(f"{field_name}={n}")
        f.value = n
        return ux, o

    def _session_ui_ctx(self):
        if ux := self.session.get("ui_ctx"):
            return ux
        self.session.ui_schema = slicops.ui_schema.load(_KIND)
        self.session.ui_ctx = ux = self.session.ui_schema.default_ui_ctx()
        ux.beam_path.valid_values = slicops.device_db.beam_paths()
        ux.beam_path.value = _cfg.dev.beam_path
        self._beam_path_change(ux, None)
        ux.camera.value = _cfg.dev.camera_name
        self._device_change(ux, None)
        return ux

    def _set_acquire(self, is_on):
        self.session.device.put("acquire", is_on)


_cfg = pkconfig.init(
    dev=PKDict(
        beam_path=("DEV_BEAM_PATH", str, "dev beampath name"),
        camera_name=("DEV_CAMERA", str, "dev camera name"),
    ),
)
