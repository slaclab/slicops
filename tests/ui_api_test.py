"""Test ui_api

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pytest


@pytest.mark.asyncio
async def test_basic():
    async with _setup() as c:
        from pykern.pkcollections import PKDict
        from pykern import pkunit, pkdebug

        ux = (await c.call_api("screen_ui_ctx", PKDict())).ui_ctx
        pkunit.pkeq("DEV_BEAM_PATH", ux.beam_path.value)
        pkunit.pkeq("DEV_CAMERA", ux.camera.value)
        pkunit.pkeq(93, ux.camera_gain.value)
        r = await c.call_api("screen_start_button", PKDict(field_value=False))
        ux = r.ui_ctx
        pkunit.pkeq(100, len(r.plot.raw_pixels))
        pkunit.pkeq(100, len(r.plot.raw_pixels[0]))
        r = await c.call_api("screen_stop_button", PKDict(field_value=False))
        ux = r.ui_ctx
        r = await c.call_api("screen_camera_gain", PKDict(field_value=33))
        ux = r.ui_ctx
        pkunit.pkeq(33, ux.camera_gain.value)


def _setup():
    from pykern import http_unit

    class _Setup(http_unit.Setup):
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

            return super()._server_config(*args, **kwargs)

        def _server_start(self, *args, **kwargs):
            from slicops.pkcli import service

            service.Commands().ui_api()

    return _Setup()