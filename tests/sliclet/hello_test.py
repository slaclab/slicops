"""Test hello

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pytest


@pytest.mark.asyncio(loop_scope="module")
async def test_status():
    from slicops import unit_util

    with unit_util.start_ioc("cam1"):
        async with unit_util.SlicletSetup("hello") as s:
            from pykern import pkunit

            r = await s.ctx_update()
            pkunit.pkeq("Initializing", r.fields.status.value)
            r = await s.ctx_update()
            pkunit.pkeq("Connected", r.fields.status.value)
            r = await s.ctx_update()
            pkunit.pkeq("Idle", r.fields.status.value)
