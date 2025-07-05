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

        r = await s.ui_ctx_update()
        pkunit.pkeq(5, r.ctx.increment.value)
        pkunit.pkeq(None, r.ctx.divisor.value)
        pkunit.pkeq("method_1", r.ctx.run_mode.value)
        pkunit.pkeq(5, r.ctx.increment.value)
        await s.ui_field_change("divisor", 1.0)
        r = await s.ui_ctx_update()
        pkunit.pkeq(["divisor"], list(r.ctx.keys()))
