"""Test screen

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pytest

_BUTTONS = tuple(f"{k}_button.ui.enabled" for k in ("start", "stop", "single"))


@pytest.mark.asyncio(loop_scope="module")
async def test_basic():
    from slicops import unit_util

    async def _buttons(s, expect, msg):
        from pykern import pkunit, pkdebug
        from pykern.pkdebug import pkdlog
        from asyncio.exceptions import CancelledError

        # Wait for buttons to "settle" on expect. The updates
        # are async so we can't control which update returns what.
        while True:
            try:
                rv = await s.ctx_update()
            except CancelledError:
                # timed out so now report mismatch via pkunit
                pkunit.pkeq(expect, v, msg)
            v = tuple(rv.fields.pknested_get(k) for k in _BUTTONS)
            if v == expect:
                break
        return rv

    with unit_util.start_ioc("ioc"):
        async with unit_util.SlicletSetup("screen") as s:
            from pykern import pkunit, pkdebug
            from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
            import asyncio
            import epics

            r = await s.ctx_update()
            pkunit.pkeq("DEV_BEAM_PATH", r.fields.beam_path.value)
            pkunit.pkeq("DEV_CAMERA", r.fields.camera.value)
            await _buttons(s, (True, False, True), "start/single enabled")
            await s.ctx_field_set(start_button=None)
            await _buttons(s, (False, False, False), "all disabled after start")
            await _buttons(s, (False, True, False), "acquire should fire")
            p = (await s.ctx_update()).fields.plot.value
            pkunit.pkeq(65, len(p.raw_pixels))
            pkunit.pkeq(50, len(p.raw_pixels[0]))
            # x fit should be 10
            pkunit.pkeq(10.00, round(p.x.fit.results.sig, 2))
            pkunit.pkeq(13.00, round(p.y.fit.results.sig, 2))
            await s.ctx_field_set(
                beam_path="CU_SPEC",
                curve_fit_method="super_gaussian",
                stop_button=None,
            )
            r = await _buttons(s, (False, False, False), "all disabled after stop")
            pkunit.pkeq(None, r.fields.camera.value)
            # there's no device so buttons on not visible
            pkunit.pkeq(False, r.fields.start_button.ui.visible)
            with pkunit.pkexcept("unknown choice"):
                await s.ctx_field_set(camera="DEV_CAMERA")
            # TODO(robnagler) better error handling await _put(ux, "camera", "DEV_CAMERA", Exception)
            await s.ctx_field_set(camera="YAG01")
            r = await s.ctx_update()
            pkunit.pkeq("YAGS:IN20:211", r.fields.pv.value)
