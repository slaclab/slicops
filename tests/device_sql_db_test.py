def test_screens_by_position():
    from pykern import pkdebug, pkunit
    from slicops import device_sql_db

    d = device_sql_db.screens_by_position("CU_HXR")

    pkunit.pkok(
        d[0] == ("VCC", 0.0),
        "Expected VCC and first at position 0",
    )
    pkunit.pkok(
        d[-1][0] == "OTRDMP",
        "Expect OTRDMP to be last",
    )
    pkunit.pkok(
        ("OTR2", 14.241) in d,
        "Expect OTR2 in the results",
    )


def test_screens_for_a_beampath():
    from pykern import pkdebug, pkunit
    from slicops import device_sql_db

    d = device_sql_db.device_names("PROF", "CU_HXR")
    pkunit.pkok(
        "OTR2" in d,
        "Missing OTR2 screen: {}",
        d,
    )


def test_screens_with_target_control_by_position():
    from pykern import pkdebug, pkunit
    from slicops import device_sql_db

    d = device_sql_db.screens_with_target_control_by_position("CU_HXR")
    pkunit.pkok(
        d[0] == ("YAG01", 0.614),
        "Expect YAG01 first at position 0.614",
    )


def test_upstream_screens():
    from pykern import pkdebug, pkunit
    from slicops import device_sql_db

    d = device_sql_db.upstream_screens("CU_HXR", "OTR2")
    pkdebug.pkdp(d)
    pkunit.pkok(
        "OTR2" not in [v[0] for v in d], "OTR2 should not be in the result list"
    )
    pkunit.pkok(
        d[-1][0] == "OTR1",
        "OTR1 should be the last screen",
    )
