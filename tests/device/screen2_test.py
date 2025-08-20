"""Test slicops.device.screen

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""


def test_upstream_blocked():
    from pykern import pkdebug, pkunit
    from slicops import unit_util

    with unit_util.setup_screen("CU_HXR", "YAG03") as s:
        s.device.move_target(want_in=True)
        e = s.handler.test_get("error")
        pkunit.pkeq("upstream", e.error_kind.name)
        pkunit.pkeq("upstream target is in", e.error_msg.YAG02)
