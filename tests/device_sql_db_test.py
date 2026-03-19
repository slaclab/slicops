"""Test device_sql_db

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern import pkunit, pkio, pkdebug
from pykern.pkcollections import PKDict


def test_upstream_screens():
    from pykern import pkdebug, pkunit
    from slicops import device_sql_db

    r = device_sql_db.upstream_screens("CU_HXR", "OTR3")
    pkunit.pkeq("YAG01", r[0], "r={}", r)
    # pkunit.pkeq(float, type(r[0][1]))
    # pkunit.pkok(0.1 < r[0][1] < 10, "not in range r[0][1]={}", r[0][1])
    pkunit.pkeq(7, len(r))
    pkunit.pkok("OTR3" not in r, "unexpected screen name={}", r)

