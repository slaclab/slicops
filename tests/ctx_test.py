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
            r = ctx.Ctx("input", "Input", path=d).as_dict()
        except Exception as e:
            pkdebug.pkdlog("{}", pkdebug.pkdexc())
            r = PKDict(error=e)
        pkjson.dump_pretty(r, filename=d.join(f"out.json"))


def test_txn():
    from pykern import pkdebug, pkjson, pkunit
    from pykern.pkcollections import PKDict
    from slicops import ctx

    c = ctx.Ctx("input", "Input", path=pkunit.data_dir().join("simple.in"))
    txn = ctx.Txn(c)
    with pkunit.pkexcept(ValueError):
        txn.field_set("increment", 0)
    txn.multi_set(
        ("run_mode.constraints.choices", ("a", "b", "c")),
        ("run_mode.value", None),
    )
    r = PKDict()
    txn.commit(lambda x: r.pkupdate(fields=x.fields))
    pkunit.pkeq(None, r.fields.run_mode.value)
    # TODO(robnagler) more tests
