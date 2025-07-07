"""Test ui_api

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pytest


@pytest.mark.asyncio(loop_scope="module")
async def test_basic():
    from slicops import unit_util

    async with unit_util.Setup("screen") as s:
        from pykern import pkunit, pkdebug
        import asyncio

        r = await s.ui_ctx_update()
        pkunit.pkeq("DEV_BEAM_PATH", r.ctx.beam_path.value)
        pkunit.pkeq("DEV_CAMERA", r.ctx.camera.value)
        return
        await _put(PKDict(field="start_button", value=False))
        r = await _plot(c)
        pkunit.pkeq(65, len(r.plot.raw_pixels))
        pkunit.pkeq(50, len(r.plot.raw_pixels[0]))
        # x fit should be 10
        pkunit.pkeq(10.00, round(r.plot.x.fit.results.sig, 2))
        pkunit.pkeq(13.00, round(r.plot.y.fit.results.sig, 2))
        r = await c.call_api("screen_stop_button", PKDict(field_value=False))
        ux = r.ui_ctx
        ux = await _put(ux, "curve_fit_method", "super_gaussian", "super_gaussian")
        ux = await _put(ux, "beam_path", "CU_SPEC", "CU_SPEC")
        pkunit.pkeq(None, ux.camera.value)
        await _put(ux, "camera", "DEV_CAMERA", Exception)
        ux = await _put(ux, "camera", "YAG01", "YAG01")
        pkunit.pkeq("YAGS:IN20:211", ux.pv.value)
