"""test basic fields

:copyright: Copyright (c) 2025 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""


def test_classes():
    from pykern.pkcollections import PKDict
    from pykern import pkunit
    from slicops import field

    p = field.prototypes()
    f = p.Button.new(PKDict(name="my_button"))
    pkunit.pkeq(None, f.value_check(None))
    f = p.Integer.new(PKDict(name="my_int"))
    pkunit.pkok(1, f.value_set("1"))
    v = f.value_check("x")
    pkunit.pkok(
        isinstance(v, field.InvalidFieldValue), "expected InvalidFieldValue={}", v
    )
    pkunit.pkeq("my_int", v.kwargs.field_name)
    f = p.Enum.new(
        PKDict(
            name="colors",
            constraints=PKDict(
                choices=PKDict(red="cyan", green="magenta", blue="yellow")
            ),
        )
    )
    pkunit.pkeq("magenta", f.value_check("green"))
    pkunit.pkeq("yellow", f.value_check("yellow"))
    v = f.value_check("x")
    pkunit.pkeq("colors", v.kwargs.field_name)
    f = f.new(PKDict(name="nums", constraints=PKDict(choices=[1, 2, 3])))
    pkunit.pkeq(PKDict({"1": 1, "2": 2, "3": 3}), f._attrs.constraints.choices)
    pkunit.pkeq(3, f.value_check(3))
    pkunit.pkeq(2, f.value_check("2"))
    pkunit.pkeq(None, f.value_check(None))
    pkunit.pkeq(None, f.value_check(""))
    r = f.value_check("4")
    pkunit.pkeq("unknown choice", r.msg)
