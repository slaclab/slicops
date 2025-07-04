"""test basic fields

:copyright: Copyright (c) 2025 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""


def test_classes():
    from pykern.pkcollections import PKDict
    from pykern import pkunit
    from slicops import field

    f = field.Button(None, PKDict())
    pkunit.pkeq(None, f.value_check(None))
    f = field.Integer(None, PKDict())
    pkunit.pkok(1, f.value_put("1"))
    v = f.value_check("x")
    pkunit.pkok(
        isinstance(v, field.InvalidFieldValue), "expected InvalidFieldValue={}", v
    )
    pkunit.pkeq("Integer", v.kwargs.field_name)
    f = field.Enum(None, PKDict())
    v = f.value_check("x")
    pkunit.pkeq("Enum", v.kwargs.field_name)
    f = f.new(PKDict(constraints=PKDict(choices=[1, 2, 3])))
    pkunit.pkeq(PKDict({"1": 1, "2": 2, "3": 3}), f._attrs.constraints.choices)
    pkunit.pkeq(3, f.value_check(3))
    pkunit.pkeq(2, f.value_check("2"))
    pkunit.pkeq(None, f.value_check(None))
    pkunit.pkeq(None, f.value_check(""))
    r = f.value_check("4")
    pkunit.pkeq("unknown choice", r.msg)
