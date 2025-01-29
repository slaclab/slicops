"""Test ui_api

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pytest


@pytest.mark.asyncio(loop_scope="module")
async def test_basic():

    async def _put(ux, field, new, expect):
        if expect == Exception:
            with pkunit.pkexcept(f"exception={field}"):
                await c.call_api(f"screen_{field}", PKDict(field_value=new))
            return
        r = await c.call_api(f"screen_{field}", PKDict(field_value=new))
        pkunit.pkeq(expect, r.ui_ctx[field].value)
        return r.ui_ctx

    async with _setup() as c:
        from pykern.pkcollections import PKDict
        from pykern import pkunit, pkdebug

        ux = (await c.call_api("screen_ui_ctx", PKDict())).ui_ctx
        pkunit.pkeq("DEV_BEAM_PATH", ux.beam_path.value)
        pkunit.pkeq("DEV_CAMERA", ux.camera.value)
        pkunit.pkeq(93, ux.camera_gain.value)
        r = await c.call_api("screen_start_button", PKDict(field_value=False))
        ux = r.ui_ctx
        pkunit.pkeq(65, len(r.plot.raw_pixels))
        pkunit.pkeq(50, len(r.plot.raw_pixels[0]))
        r = await c.call_api("screen_stop_button", PKDict(field_value=False))
        ux = r.ui_ctx
        ux = await _put(ux, "camera_gain", "33", 33)
        ux = await _put(ux, "curve_fit_method", "super_gaussian", "super_gaussian")
        await _put(ux, "camera_gain", 999999, Exception)
        ux = await _put(ux, "camera_gain", 99, 99)
        ux = await _put(ux, "beam_path", "CU_SPEC", "CU_SPEC")
        pkunit.pkeq(None, ux.camera.value)
        await _put(ux, "camera", "DEV_CAMERA", Exception)
        ux = await _put(ux, "camera", "YAG01", "YAG01")
        pkunit.pkeq("YAGS:IN20:211", ux.pv.value)


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
