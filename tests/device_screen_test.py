"""Test slicops.device

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""


def test_target():
    # Must be first
    from slicops import mock_epics
    from pykern import pkdebug, pkunit
    from slicops import device_screen
    import time

    status = None

    def _status(update):
        nonlocal status

        if "connected" in update:
            return
        status = update.value

    mock_epics.reset_state()
    d = None
    try:
        d = device_screen.Screen("OTRDG04")
        pkunit.pkeq(1, d.accessor("target_status").get())
        d.insert_target()
        pkunit.pkeq(2, d.accessor("target_status").get())
        return
        pkunit.pkeq(False, d.get("acquire"))
        s = d.accessor("target_status")
        s.monitor(_status)
        time.sleep(0.1)
        pkunit.pkeq(1, status)
        c = d.accessor("target_control")
        c.put(1)
        time.sleep(0.1)
        pkunit.pkeq(2, status)
    finally:
        if d:
            d.destroy()
