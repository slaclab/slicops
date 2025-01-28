"""Screen (Profile Monitor) UI API

`API` stores ``ui_ctx`` (UI Context, local var ``ux``) in the
`pykern.http.Session`. The ``ui_ctx`` is a mirror of all state in the
client. Calls to this `API` changes the ``ui_ctx`` and possibly
invokes changes to the underlying device, also stored in the
`Session`.

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern import pkconfig, pkresource, pkyaml
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import asyncio
import lcls_tools.common.data.fitting_tool
import numpy
import random
import slicops.device
import slicops.device_db
import slicops.quest
import time

_KIND = "screen"

_cfg = None

_FIELD_VALIDATOR = None

_FIELD_DEFAULT = None


class InvalidFieldValue(RuntimeError):

    pass


class API(slicops.quest.API):
    """Implementation for the Screen (Profile Monitor) application"""

    async def api_screen_beam_path(self, api_args):
        """Set the ``beam_path``"""
        ux, o, c = self._save_field("beam_path", api_args)
        if c:
            self._beam_path_change(ux, o)
        # TODO(pjm): could return a diff of model changes rather than full model
        # OK to return in place values, not copy, becasue
        return self._return(ux)

    async def api_screen_camera(self, api_args):
        """Set the ``camera`` which may change the ``device``"""
        ux, o, c = self._save_field("camera", api_args)
        if c:
            self._device_change(ux, o)
        return self._return(ux)

    async def api_screen_camera_gain(self, api_args):
        ux, _, _ = self._save_field("camera_gain", api_args)
        self.session.device.put("gain", ux.camera_gain.value)
        return self._return(ux)

    async def api_screen_color_map(self, api_args):
        ux, _, _ = self._save_field("color_map", api_args)
        return self._return(ux)

    async def api_screen_curve_fit_method(self, api_args):
        ux, _, _ = self._save_field("curve_fit_method", api_args)
        return await self._return_with_image(ux)

    async def api_screen_plot(self, api_args):
        return await self._return_with_image(self._session_ui_ctx())

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
        ux.plot.auto_refresh = True
        return await self._return_with_image(ux)

    async def api_screen_stop_button(self, api_args):
        ux = self._session_ui_ctx()
        ux.plot.auto_refresh = False
        self._set_acquire(0)
        self._button_setup(ux, False)
        return self._return(ux)

    async def api_screen_ui_ctx(self, api_args):
        ux = self._session_ui_ctx()
        # TODO(robnagler) if accepting ui_ctx, then need to update valid_values here
        return self._return(ux).pkupdate(
            # TODO(pjm): need a better way to load a resource for a sliclet
            layout=pkyaml.load_file(pkresource.file_path("static/layout/screen.yaml")),
        )

    def _beam_path_change(self, ux, old_name):
        # TODO(robnagler) get from device db
        ux.camera.choices = _choice_map(
            slicops.device_db.devices_for_beam_path(ux.beam_path.value, _KIND),
        )
        if (
            _validate_field(ux.camera, ux.camera.value) is not None
            or (o := ux.camera.value) is None
        ):
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
            self._button_setup(ux, False)

        def _destroy():
            if not old_name or not (d := self.session.get("device")):
                return
            try:
                self._set_acquire(0)
            except Exception as e:
                pkdlog(
                    "set acquire=0 PV error={} device={} stack={}", e, d.name, pkdexc()
                )
            self.session.device = None
            d.destroy()

        def _setup():
            d = self.session.device = slicops.device.Device(ux.camera.value)
            if d.has_accessor("gain"):
                ux.camera_gain.value = d.get("gain")
            else:
                # TODO(robnagler) enabled?
                ux.camera_gain.value = None
            ux.pv.value = d.meta.pv_prefix
            a = _acquiring(d)
            self._button_setup(ux, a)
            ux.plot.auto_refresh = a

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
            ux.curve_fit_method.visible = True
            ux.color_map.visible = True
            return PKDict(
                lineout=profile.tolist(),
                fit=PKDict(
                    fit_line=getattr(tool, method)(x=tool.x, **p).tolist(),
                    results=p,
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
        f = ux[field_name]
        if (n := _validate_field(f, api_args.field_value)) is None:
            # TODO(robnagler) better error messages
            raise InvalidFieldValue(f"{field_name}={api_args.field_value}")
        if (o := f.value) == n:
            return ux, None, False
        f.value = n
        return ux, o, True

    def _session_ui_ctx(self):
        if ux := self.session.get("ui_ctx"):
            return ux
        self.session.ui_ctx = ux = _ui_ctx_default()
        ux.beam_path.value = _cfg.dev.beam_path
        self._beam_path_change(ux, None)
        ux.camera.value = _cfg.dev.camera_name
        self._device_change(ux, None)
        return ux

    def _set_acquire(self, is_on):
        if d := self.session.get("device"):
            d.put("acquire", is_on)


def _choice_map(values):
    def _values():
        if isinstance(values[0], (tuple, list)):
            return values
        return zip(values, values)

    return tuple((PKDict(code=v[0], display=v[1]) for v in _values()))


def _choice_validator(field, value):
    for v in field.choices:
        if v.code == value:
            return value
    return None


def _gain_validator(field, value):
    try:
        rv = int(value)
    except Exception:
        return None
    return rv if 0 <= rv <= 1000 else None


def _init():
    global _cfg, _FIELD_VALIDATOR, _FIELD_DEFAULT

    _cfg = pkconfig.init(
        dev=PKDict(
            beam_path=("DEV_BEAM_PATH", str, "dev beam path name"),
            camera_name=("DEV_CAMERA", str, "dev camera name"),
        ),
    )
    _FIELD_VALIDATOR = PKDict(
        # TODO(pjm): validators could be based on field type
        beam_path=_choice_validator,
        camera=_choice_validator,
        camera_gain=_gain_validator,
        color_map=_choice_validator,
        curve_fit_method=_choice_validator,
    )

    _FIELD_DEFAULT = pkyaml.load_file(pkresource.file_path("static/schema/screen.yaml"))


def _ui_ctx_default():
    # TODO(robnagler): return an object

    def _value(name):
        return _FIELD_DEFAULT.get(name, PKDict()).pksetdefault(
            enabled=True,
            name=name,
            value=None,
            visible=True,
        )

    return PKDict({n: _value(n) for n in _FIELD_DEFAULT.keys()})


def _validate_field(field, value):
    if p := _FIELD_VALIDATOR.get(field.name):
        return p(field, value)
    return value


_init()
