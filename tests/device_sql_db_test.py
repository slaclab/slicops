
def test_screens_for_a_beampath():
    from pykern import pkdebug, pkunit
    from slicops import device_sql_db

    d = device_sql_db.device_names("PROF", "CU_HXR")
    pkunit.pkok(
        "OTR2" in d,
        "Missing OTR2 screen: {}",
        d,
    )
