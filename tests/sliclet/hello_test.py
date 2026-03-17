"""Test hello

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pytest

# asyncio/async/await is boilerplate
@pytest.mark.asyncio(loop_scope="module")
async def test_greeting():
    from slicops import mock_epics
    mock_epics.reset_state()
    from slicops import unit_util
    # starts tornado and vite on unique ports; shuts down
    async with unit_util.SlicletSetup("hello") as s:
        # provides lots of useful utilities, for now comparison
        from pykern import pkunit
        # get first ctx_update; vuew bootstraps: all fields and ui_layout
        r = await s.ctx_update()
        pkunit.pkeq("Hello World!", r.fields.message.value)
        # click greeting button (value required and must be None)
        await s.ctx_field_value_set(greeting=None)
        # next update should contain changed message
        r = await s.ctx_update()
        pkunit.pkre(r"Ta Ta! \d+", r.fields.message.value)

