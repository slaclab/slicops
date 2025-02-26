"""Test slicops.device

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""


def test_basic():
    # Must be first
    from slicops import mock_epics
    from pykern.pkunit import pkeq
    from slicops import device

    mock_epics.reset_state()
    d = device.Device("DEV_CAMERA")
    # Reshape switches x & y
    pkeq((65, 50), d.get("image").shape)
    pkeq(False, d.get("acquire"))
    d.put("acquire", True)
    pkeq(True, d.get("acquire"))


def test_monitor():
    # Must be first
    from slicops import mock_epics
    from pykern import pkdebug
    from pykern.pkunit import pkeq, pkfail
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
            pkeq(True, update.connected)
        elif connected:
            # disconnects after connected
            pkeq(False, update.connected)
        else:
            pkfail("connected is already false update={}", update)
        connected = update.connected

    def _monitor(update):
        nonlocal x_size, count, connected

        if "connected" in update:
            _connected(update)
            return
        # reshape will switch x & y
        pkeq(x_size.pop(), update.value.shape[1])
        count -= 1

    a = device.Device("DEV_CAMERA").accessor("image")
    a.monitor(_monitor)
    time.sleep(count * 2 * mock_epics.MONITOR_SLEEP)
    pkeq(0, count)
    pkeq(False, connected)
