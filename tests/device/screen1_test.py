"""Test slicops.device.screen

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from slicops import unit_util


def test_upstream_ok():
    from pykern import pkdebug, pkunit

    with unit_util.setup_screen("CU_HXR", "YAG03") as s:
        s.handler.test_get("image")
        pkunit.pkeq(False, s.handler.test_get("acquire"))
        pkunit.pkeq(False, s.handler.test_get("target_status"))
        s.device.move_target(want_in=True)
        pkunit.pkeq(True, s.handler.test_get("target_status"))
        s.device.move_target(want_in=False)
        pkunit.pkeq(False, s.handler.test_get("target_status"))
