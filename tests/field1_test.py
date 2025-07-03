"""test basic fields

:copyright: Copyright (c) 2025 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""


def test_standard():
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
