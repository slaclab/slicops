"""test ctx

:copyright: Copyright (c) 2025 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""


def test_cases():
    from pykern import pkdebug, pkjson, pkunit
    from pykern.pkcollections import PKDict
    from slicops import ctx

    for d in pkunit.case_dirs():
        try:
            r = ctx.Ctx("input", path=d).as_dict()
        except Exception as e:
            pkdebug.pkdlog("{}", pkdebug.pkdexc())
            r = PKDict(error=e)
        pkjson.dump_pretty(r, filename=d.join(f"out.json"))


def test_txn():
    from pykern import pkdebug, pkjson, pkunit
    from pykern.pkcollections import PKDict
    from slicops import ctx

    c = ctx.Ctx("input", path=pkunit.data_dir().join("simple.in"))
    txn = ctx.Txn(c)
    with pkunit.pkexcept(ValueError):
        txn.field_set("increment", 0)
