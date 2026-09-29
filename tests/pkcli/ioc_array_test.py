"""Test ioc array writes

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""


def test_array_put():
    from slicops import unit_util

    with unit_util.start_ioc("init.yaml", db_yaml="db.yaml"):
        from pykern import pkunit
        import epics

        p = epics.PV("ARRAY:TEST", auto_monitor=False)
        try:
            pkunit.pkok(p.wait_for_connection(timeout=5), "no connection")
            pkunit.pkok(p.put([1.0, 2.0, 3.0], wait=True, timeout=5), "put failed")
            pkunit.pkeq([1.0, 2.0, 3.0], p.get(timeout=5).tolist())
            pkunit.pkeq(
                "ARRAY:TEST:\n  - 1.0\n  - 2.0\n  - 3.0\n",
                pkunit.work_dir().join("db.yaml").read("rt"),
            )
        finally:
            p.disconnect()
