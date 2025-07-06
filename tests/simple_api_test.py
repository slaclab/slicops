"""Support for unit tests

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pytest


@pytest.mark.asyncio(loop_scope="module")
async def test_basic():
    from slicops import unit_util

    async with unit_util.Setup("simple") as s:
        from pykern import pkunit, pkdebug
        from slicops.pkcli import simple
        import asyncio

        r = await s.ui_ctx_update()
        pkunit.pkeq(5, r.fields.increment.value)
        pkunit.pkeq(None, r.fields.divisor.value)
        pkunit.pkeq("method_1", r.fields.run_mode.value)
        pkunit.pkeq(5, r.fields.increment.value)
        await s.ui_ctx_write(divisor=1.0)
        r = await s.ui_ctx_update()
        pkunit.pkeq(["divisor"], list(r.fields.keys()))
        pkunit.pkeq(1.0, r.fields.divisor.value)
        pkunit.pkeq(None, simple.read().divisor)
        await s.ui_ctx_write(save_button=None)
        # write happens async and there's no db until we start
        await asyncio.sleep(0.5)
        pkunit.pkeq(1.0, simple.read().divisor)
        # no update client side
        simple.write("divisor=3")
        r = await s.ui_ctx_update()
        pkunit.pkeq(3.0, r.fields.divisor.value)
        await s.ui_ctx_write(run_mode="method_2")
        r = await s.ui_ctx_update()
        await s.ui_ctx_write(revert_button=None)
        # no update, bc no change
        pkunit.pkeq("method_1", simple.read().run_mode)
