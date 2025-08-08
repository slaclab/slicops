"""Test ioc

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

_DB = """WIRE:HTR:340:MOTR_ENABLED_STS: {}
WIRE:HTR:340:STARTSCAN: {}
"""


def test_db_yaml():
    from slicops import unit_util

    with unit_util.start_ioc("init.yaml", db_yaml="db.yaml"):
        from slicops import device
        from pykern import pkdebug, pkunit
        import time

        b = pkunit.work_dir().join("db.yaml")
        d = device.Device("WS0H04")
        try:
            pkunit.pkeq(33, d.get("enabled"))
            pkunit.pkeq(_DB.format(33, 0), b.read("rt"))
            d.put("start_scan", 1)
            # Allow the dispatch to come back
            time.sleep(0.1)
            pkunit.pkeq(66, d.get("enabled"))
            pkunit.pkeq(_DB.format(66, 1), b.read("rt"))
        finally:
            d.destroy()
