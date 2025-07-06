"""Support for unit tests

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

# limit imports that might touch config
import asyncio
import pykern.api.unit_util


class Setup(pykern.api.unit_util.Setup):
    def __init__(self, sliclet, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__sliclet = sliclet
        self.__update_q = asyncio.Queue()

    async def ui_ctx_update(self):
        from pykern import pkunit

        r = await self.__update_q.get()
        self.__update_q.task_done()
        if r is None:
            pkunit.pkfail("subscription ended unexpectedly")
        return r

    async def ui_ctx_write(self, **kwargs):
        from pykern.pkcollections import PKDict
        from pykern import pkdebug

        await self.client.call_api(
            "ui_ctx_write", pkdebug.pkdp(PKDict(field_values=PKDict(kwargs)))
        )

    async def __aenter__(self):
        await super().__aenter__()
        asyncio.create_task(self.__subscribe())
        return self

    def _global_config(self, **kwargs):
        from pykern import util

        return super()._global_config(
            SLICOPS_CONFIG_UI_API_TCP_PORT=str(util.unbound_localhost_tcp_port()),
            **kwargs,
        )

    def _http_config(self, *args, **kwargs):
        from slicops import config

        return config.cfg().ui_api.copy()

    def _server_config(self, *args, **kwargs):
        from slicops import mock_epics

        mock_epics.reset_state()

        return super()._server_config(*args, **kwargs)

    def _server_start(self, *args, **kwargs):
        from slicops.pkcli import service

        service.Commands().ui_api()

    async def __subscribe(self):
        from pykern import pkdebug
        from pykern.pkcollections import PKDict
        from pykern.api import util

        try:
            with await self.client.subscribe_api(
                "ui_ctx_update", PKDict(sliclet=self.__sliclet)
            ) as s:
                while True:
                    r = await s.result_get()
                    self.__update_q.put_nowait(r)
                    if r is None:
                        return
        except util.APIDisconnected:
            pkdebug.pkdlog("APIDisconnected sliclet={}", self.__sliclet)
        except Exception as e:
            pkdebug.pkdlog("error={} stack={}", e, pkdebug.pkdexc())
            raise
