"""Simple file based UI API

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern import pkconfig, pkresource, pkyaml
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import asyncio
import pykern.api.util
import slicops.device
import slicops.device_db
import slicops.quest
import slicops.pkcli.simple

_UI_CTX_KEY = "ui_ctx"
_UPDATE_Q_KEY = "update_q"
_FIELD_DEFAULT = None

# TODO(pjm): too much boilerplate for an app, copy/pasted from screen.py for now


class API(slicops.quest.API):
    """Implementation for the Simple application"""

    async def api_simple_save_button(self, api_args):
        def _values(ux):
            return ((f.name, f.value) for f in ux.values() if f.widget != "button")

        ux = self._session_ui_ctx()
        slicops.pkcli.simple.write(PKDict(_values(ux)))
        return self._return(ux)

    async def api_simple_revert_button(self, api_args):
        ux = self._session_ui_ctx()
        self._read_db(ux)
        return self._return(ux)

    async def api_simple_run_mode(self, api_args):
        ux, _, _ = self._save_field("run_mode", api_args)
        return self._return(ux)

    async def api_simple_increment(self, api_args):
        ux, _, _ = self._save_field("increment", api_args)
        return self._return(ux)

    async def api_simple_ui_ctx(self, api_args):
        ux = self._session_ui_ctx()
        return self._return(ux).pkupdate(
            layout=pkyaml.load_file(pkresource.file_path("layout/simple.yaml")),
        )

    @pykern.api.util.subscription
    async def api_simple_update(self, api_args):
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

    def _read_db(self, ux):
        for k, v in slicops.pkcli.simple.read().items():
            if k in ux:
                ux[k].value = v

    def _return(self, ux):
        return PKDict(ui_ctx=ux)

    def _save_field(self, field_name, api_args):
        ux = self._session_ui_ctx()
        f = ux[field_name]
        f.value = api_args.field_value
        return ux, None, True

    def _session_ui_ctx(self):
        if ux := self.session.get(_UI_CTX_KEY):
            return ux
        self.session.ui_ctx = ux = _ui_ctx_default()
        self._read_db(ux)
        return ux


class _Field(PKDict):
    pass


class _UIContext(PKDict):
    pass


def _init():
    global _FIELD_DEFAULT
    _FIELD_DEFAULT = pkyaml.load_file(pkresource.file_path("schema/simple.yaml"))


def _ui_ctx_default():
    def _value(name):
        return _Field(_FIELD_DEFAULT[name]).pksetdefault(
            enabled=True,
            name=name,
            value=None,
            visible=True,
        )

    return _UIContext({n: _value(n) for n in _FIELD_DEFAULT.keys()})


_init()
