"""Test hello

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pytest


@pytest.mark.asyncio(loop_scope="module")
async def test_greeting():
    from slicops import unit_util

    async with unit_util.SlicletSetup("hello") as s:
        from pykern import pkunit

        r = await s.ctx_update()
        pkunit.pkeq(r"Hello World!", r.fields.message.value)
        
        await s.ctx_field_value_set(greeting=None)
        
        r = await s.ctx_update()
        pkunit.pkre(r"Ta Ta! \d+", r.fields.message.value)
        pass
