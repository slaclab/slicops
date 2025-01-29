"""Test slicops.device

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""


def test_basic():
    # Must be first
    from slicops import mock_epics
    from pykern import pkdebug, pkunit
    from slicops import device

    mock_epics.reset_state()
    d = device.Device("DEV_CAMERA")
    # Reshape switches x & y
    pkunit.pkeq((65, 50), d.get("image").shape)
    pkunit.pkeq(False, d.get("acquire"))
    d.put("acquire", True)
    pkunit.pkeq(True, d.get("acquire"))


def test_monitor():
    # Must be first
    from slicops import mock_epics
    from pykern import pkdebug, pkunit
    from slicops import device
    import time

    mock_epics.reset_state()
    x_size = list(reversed(mock_epics.MONITOR_X_SIZE))
    count = len(x_size)
    connected = None

    def _connected(update):
        nonlocal connected

        if connected is None:
            # starting: gets connected
            pkunit.pkeq(True, update.connected)
            connected = True
        elif connected:
            # disconnects after connected
            pkunit.pkeq(False, update.connected)
            connected = False
        else:
            pkunit.pkfail("connected is already false update={}", update)

    def _monitor(update):
        nonlocal x_size, count, connected

        if "connected" in update:
            _connected(update)
            return
        # reshape will switch x & y
        pkunit.pkeq(x_size.pop(), update.value.shape[1])
        count -= 1

    a = device.Device("DEV_CAMERA").accessor("image")
    a.monitor(_monitor)
    time.sleep(count * 2 * mock_epics.MONITOR_SLEEP)
    pkunit.pkeq(0, count)
    pkunit.pkeq(False, connected)
