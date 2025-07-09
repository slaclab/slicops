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

        r = await s.ctx_update()
        pkunit.pkeq(5, r.fields.increment.value)
        pkunit.pkeq(3.14, r.fields.divisor.value)
        pkunit.pkeq("method_1", r.fields.run_mode.value)
        pkunit.pkeq(5, r.fields.increment.value)
        await s.ctx_field_set(divisor=1.1)
        r = await s.ctx_update()
        pkunit.pkeq(["divisor"], list(r.fields.keys()))
        pkunit.pkeq(1.1, r.fields.divisor.value)
        pkunit.pkeq(3.14, simple.read("simple").divisor)
        r = await s.ctx_field_set(save=None)
        # save button
        await s.ctx_update()
        pkunit.pkeq(1.1, simple.read("simple").divisor)
        # no update client side
        simple.write("simple", "divisor=3")
        r = await s.ctx_update()
        pkunit.pkeq(3.0, r.fields.divisor.value)
        await s.ctx_field_set(run_mode="method_2")
        r = await s.ctx_update()
        await s.ctx_field_set(revert=None)
        await s.ctx_update()
        # no update, bc no change
        pkunit.pkeq("method_1", simple.read("simple").run_mode)
