"""Test slicops.device_db

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""


def test_basic():
    from pykern import pkdebug, pkunit
    from slicops import device_db
    import numpy

    a = device_db.beam_paths()
    pkunit.pkeq("CU_ALINE", a[0])
    pkunit.pkeq("SC_SXR", a[-1])
    pkunit.pkeq(18, len(a))

    a = device_db.device_names("PROF", "SC_SXR")
    pkunit.pkeq("BOD10", a[0])
    pkunit.pkeq("YAGH2", a[-1])
    pkunit.pkeq(11, len(a))
    with pkunit.pkexcept("XYZZY"):
        device_db.device_names("PROF", "XYZZY")
    with pkunit.pkexcept("xyzzy"):
        device_db.device_names("xyzzy", "SC_SXR")

    a = device_db.meta_for_device("VCCB")
    pkunit.pkeq("CAMR:LGUN:950:Image:ArrayData", a.accessor.image.pv_name)
    pkunit.pkeq(numpy.ndarray, a.accessor.image.py_type)
    pkunit.pkeq("GUNB", a.beam_area)

    # YAG01B does not have any PVs so not in db
    with pkunit.pkexcept("NoRows"):
        device_db.meta_for_device("YAG01B")


def test_upstream():
    from pykern import pkdebug, pkunit
    from slicops import device_db

    a = device_db.upstream_devices("PROF", "target_control", "CU_HXR", "OTR11")
    pkunit.pkeq(9, len(a))
    pkunit.pkeq("YAG01", a[0], "Lowest Z Prof")
    pkunit.pkeq("OTR4", a[-1], "Closest Z Prof")
