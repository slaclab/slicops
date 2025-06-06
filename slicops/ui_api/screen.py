"""Screen (Profile Monitor) UI API

`API` stores ``ui_ctx`` (UI Context, local var ``ux``) in the
`pykern.api.server.Session`. The ``ui_ctx`` is a mirror of all state in the
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
import numpy
import pykern.api.util
import pykern.util
import scipy.optimize
import slicops.device
import slicops.device_db
import slicops.quest

_KIND = "screen"

_cfg = None

_FIELD_VALIDATOR = None

_FIELD_DEFAULT = None

_DEVICE_KEY = "device"
_PLOT_KEY = "plot"
_MONITOR_KEY = "monitor"

_UI_CTX_KEY = "ui_ctx"

_UPDATE_Q_KEY = "update_q"

_SINGLE_BUTTON_Q_KEY = "single_button_q"


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
        try:
            self.session[_DEVICE_KEY].put("gain", ux.camera_gain.value)
        except slicops.device.DeviceError as e:
            pkdlog("error={} on {}; stack={}", e, d, pkdexc())
            raise pykern.util.APIError(e)
        return self._return(ux)

    async def api_screen_color_map(self, api_args):
        ux, _, _ = self._save_field("color_map", api_args)
        return self._return(ux)

    async def api_screen_curve_fit_method(self, api_args):
        ux, _, _ = self._save_field("curve_fit_method", api_args)
        # TODO(robnagler) if acquiring just wait for next image?
        return self._return_with_plot(ux)

    async def api_screen_plot(self, api_args):
        return PKDict()

    async def api_screen_single_button(self, api_args):
        if self.session.get(_SINGLE_BUTTON_Q_KEY):
            raise RuntimeError("single_button already pressed")
        ux = self._session_ui_ctx()
        # make sure q is there before acquiring
        q = self.session[_SINGLE_BUTTON_Q_KEY] = asyncio.Queue()
        # TODO(robnagler) buttons should always change and be sent back,
        # because image acquisition could take time.
        try:
            self._set_acquire(1)
            rv = await q.get()
            q.task_done()
            return rv
        finally:
            self.session.pkdel(_SINGLE_BUTTON_Q_KEY)
            try:
                # TODO(robnagler) if raised, then ignore errors here. First error is returned
                self._set_acquire(0)
            except Exception as e:
                pkdlog(
                    "ignoring error={} on {}; stack={}",
                    e,
                    self.session.get(_DEVICE_KEY),
                    pkdexc(),
                )

    async def api_screen_start_button(self, api_args):
        ux = self._session_ui_ctx()
        self._set_acquire(1)
        self._button_setup(ux, True)
        return self._return(ux)

    async def api_screen_stop_button(self, api_args):
        ux = self._session_ui_ctx()
        self._set_acquire(0)
        self._button_setup(ux, False)
        return self._return(ux)

    async def api_screen_ui_ctx(self, api_args):
        ux = self._session_ui_ctx()
        # TODO(robnagler) if accepting ui_ctx, then need to update valid_values here
        return self._return(ux).pkupdate(
            # TODO(pjm): need a better way to load a resource for a sliclet
            layout=pkyaml.load_file(pkresource.file_path("layout/screen.yaml")),
        )

    @pykern.api.util.subscription
    async def api_screen_update(self, api_args):
        if self.session.get(_UPDATE_Q_KEY):
            raise RuntimeError("already updating")
        try:
            q = self.session[_UPDATE_Q_KEY] = asyncio.Queue()
            while not self.is_quest_end():
                r = await q.get()
                q.task_done()
                if r is None:
                    return None
                self.subscription.result_put(r)
        finally:
            if "session" in self:
                self.session.pkdel(_UPDATE_Q_KEY)

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
            # must be robust, used in "except:"
            ux.camera_gain.value = None
            ux.pv.value = None
            self._button_setup(ux, False)

        def _destroy():
            if not old_name or not (d := self.session.get(_DEVICE_KEY)):
                return
            try:
                self._set_acquire(0)
            except Exception as e:
                pkdlog(
                    "set acquire=0 PV error={} device={} stack={}", e, d.name, pkdexc()
                )
            self.session[_DEVICE_KEY] = None
            _Monitor.destroy(self.session)
            d.destroy()

        def _setup():
            d = None
            try:
                d = self.session[_DEVICE_KEY] = slicops.device.Device(ux.camera.value)
                if d.has_accessor("gain"):
                    ux.camera_gain.value = d.get("gain")
                else:
                    # TODO(robnagler) enabled?
                    ux.camera_gain.value = None
                ux.pv.value = d.meta.pv_prefix
                self._button_setup(ux, _acquiring(d))
                d.accessor("image").monitor(_Monitor(self.session))
            except slicops.device.DeviceError as e:
                pkdlog("error={} on {}, clearing camera; stack={}", e, d, pkdexc())
                ux.camera.value = None
                _clear()
                raise pykern.util.APIError(e)

        _destroy()
        if ux.camera.value is None:
            _clear()
            return
        _setup()

    def _return(self, ux):
        return PKDict(ui_ctx=ux)

    def _return_with_plot(self, ux):
        rv = self._return(ux)
        if p := self.session.get(_PLOT_KEY):
            r = p.api_result(ux)
            if q := self.session.get(_UPDATE_Q_KEY):
                q.put_nowait(r)
            else:
                # TODO(robnagler) this shouldn't ever happen, but good for ui_api_test
                rv.pkupdate(r)
        return rv

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
        if ux := self.session.get(_UI_CTX_KEY):
            return ux
        self.session.ui_ctx = ux = _ui_ctx_default()
        ux.beam_path.value = _cfg.dev.beam_path
        self._beam_path_change(ux, None)
        ux.camera.value = _cfg.dev.camera
        # This will reset the camera if it is not working, but no error
        try:
            self._device_change(ux, None)
        except pykern.util.APIError:
            # TODO(robnagler): UI has to boot display the error
            # but it doesn't have a context to render.
            # Perhaps it should start without an initial camera
            # and then set the camera on the next call. Hard to program
            pass
        return ux

    def _set_acquire(self, is_on):
        if d := self.session.get(_DEVICE_KEY):
            try:
                d.put("acquire", is_on)
            except slicops.device.DeviceError as e:
                pkdlog("error={} on {}, clearing camera; stack={}", e, d, pkdexc())
                raise pykern.util.APIError(e)


class _Field(PKDict):
    pass


class _Monitor:
    # TODO(robnagler) handle more values besides plot
    def __init__(self, session):
        self._destroyed = False
        self.session = session
        self.session[_MONITOR_KEY] = self
        self.session[_PLOT_KEY] = _Plot()
        self.loop = asyncio.get_event_loop()

    def session_end(self):
        if self._destroyed:
            return
        self._destroyed = True
        if d := self.session.get(_DEVICE_KEY):
            self.session[_DEVICE_KEY] = None
            d.destroy()
        self.session.pkdel(_MONITOR_KEY)
        self.session.pkdel(_PLOT_KEY)
        self.session = None

    def __call__(self, change):
        if self._destroyed:
            return
        if e := change.get("error"):
            pkdlog("error={} on {}", e, change.get("accessor"))
            return
        if (v := change.get("value")) is not None:
            self.loop.call_soon_threadsafe(self._update, v)

    @classmethod
    def destroy(cls, session):
        if self := session.pkdel(_MONITOR_KEY):
            self.session_end()

    def _update(self, image):
        try:
            self.session[_PLOT_KEY].image = image
            if q := self.session.get(_UPDATE_Q_KEY):
                q.put_nowait(
                    self.session[_PLOT_KEY].api_result(self.session.get(_UI_CTX_KEY)),
                )
            if q := self.session.get(_SINGLE_BUTTON_Q_KEY):
                # Any value is fine
                q.put_nowait(True)
        except Exception as e:
            pkdlog("error={} stack={}", e, pkdexc())
            raise


class _Plot:
    def __init__(self):
        self.image = None

    def api_result(self, ux):
        if self.image is None:
            return PKDict()
        rv = PKDict(
            plot=PKDict(
                raw_pixels=self.image,
                x=self._fit(ux, self.image.sum(axis=0)),
                y=self._fit(ux, self.image.sum(axis=1)[::-1]),
            ),
        )
        if not (ux.curve_fit_method.visible and ux.color_map.visible):
            ux.curve_fit_method.visible = True
            ux.color_map.visible = True
            rv.ui_ctx = ux
        return rv

    def _fit(self, ux, profile):
        """Use the scipy curve_fit() to match the selected method.
        Valid methods are (gaussian, super_gaussian).
        """

        def gaussian(x, amplitude, mean, sigma, offset):
            return amplitude * numpy.exp(-(((x - mean) / sigma) ** 2) / 2) + offset

        def super_gaussian(x, amplitude, mean, sigma, offset, p):
            return amplitude * numpy.exp(-numpy.abs((x - mean) / sigma) ** p) + offset

        popt = None
        dist_keys = ["amp", "mean", "sig", "offset"]
        # TODO(pjm): should use physical camera dimensions
        x = numpy.arange(len(profile))
        try:
            m = gaussian
            popt, pcov = scipy.optimize.curve_fit(m, x, profile)
            if ux.curve_fit_method.value == "super_gaussian":
                # use gaussian fit to guess other distribution starting values
                m = super_gaussian
                dist_keys = ["amp", "mean", "sig", "offset", "p"]
                popt, pcov = scipy.optimize.curve_fit(
                    m, x, profile, p0=numpy.append(popt, 1.1)
                )
            fit_line = m(x, *popt)
        except RuntimeError as e:
            # TODO(pjm): show fitting error message on curve fit method field
            fit_line = numpy.zeros(len(x))
        return PKDict(
            lineout=profile,
            fit=PKDict(
                fit_line=fit_line,
                results=None if popt is None else dict(zip(dist_keys, popt)),
            ),
        )


class _UIContext(PKDict):
    pass


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
    # TODO(pjm): use min/max values from schema/screen.yaml
    return rv if 10 <= rv <= 1000 else None


def _init():
    global _cfg, _FIELD_VALIDATOR, _FIELD_DEFAULT

    _cfg = pkconfig.init(
        dev=PKDict(
            beam_path=("DEV_BEAM_PATH", str, "dev beam path name"),
            camera=("DEV_CAMERA", str, "dev camera name"),
        ),
    )
    _FIELD_VALIDATOR = PKDict(
        # TODO(pjm): validators could be based on field widget
        beam_path=_choice_validator,
        camera=_choice_validator,
        camera_gain=_gain_validator,
        color_map=_choice_validator,
        curve_fit_method=_choice_validator,
    )

    _FIELD_DEFAULT = pkyaml.load_file(pkresource.file_path("schema/screen.yaml"))
    _FIELD_DEFAULT.beam_path.choices = _choice_map(slicops.device_db.beam_paths())


def _ui_ctx_default():
    # TODO(robnagler): return an object

    def _value(name):
        return _Field(_FIELD_DEFAULT[name]).pksetdefault(
            enabled=True,
            name=name,
            value=None,
            visible=True,
        )

    return _UIContext({n: _value(n) for n in _FIELD_DEFAULT.keys()})


def _validate_field(field, value):
    if p := _FIELD_VALIDATOR.get(field.name):
        return p(field, value)
    return value


_init()
