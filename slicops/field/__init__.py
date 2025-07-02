"""Ctx Value

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern import pkconfig, pkresource, pkyaml
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import pykern.pkinspect


class InvalidFieldValue:
    def __init__(self, msg, **kwargs):
        self.msg = msg
        self.kwargs = PKDict(kwargs)

    def __str__(self):
        def _values():
            for k in sorted(self.kwargs.keys()):
                try:
                    yield f"{k}={str(self.kwargs[v]):.500}"
                except:
                    # TODO(robnagler) may be not the best
                    pass
        try:
            return str(self.msg) + " " + " ".join(_values())
        except:
            return super().__str__()


class Base:
    __TOP_ATTRS = frozenset(("constraints", "name", "ui", "value"))

    def _defaults(self, *overrides):
        rv = PKDict(
            constraints=PKDict(max=None, min=None, nullable=True),
            name=None,
            ui=PKDict(label=None, widget=None, writable=True),
            value=None,
        )
        for o in overrides:
            rv.pkmerge(o, make_copy=False)
        return self._assert_attrs(rv)

    def __init__(self, overrides):
        if a := getattr(self, "_attrs", None):
            a = copy.deepcopy(a)
        else:
            a = self._defaults()
        a.pkmerge(overrides, make_copy=False)
        self._attrs = self._assert_attrs(a)
        v = self.value_check(self._attrs.value)
        if isinstance(v, InvalidFieldValue):
            raise ValueError(v)
        self._attrs.value = v

    def value_check(self, value):
        if value is None:
            if self._attrs.constraints.nullable:
                return None
            rv = InvalidValue(msg="None")
        else:
            v = self._from_literal(self._attrs.value)
            if not isinstance(v, InvalidFieldValue):
                return v
            rv = v
        rv.kwargs.field_name = self._attrs.name
        return v

    def value_get(self):
        return self._attrs.value

    def value_put(self, value):
        v = self.value_check(value)
        if isinstance(v, InvalidFieldValue):
            return v
        self._attrs.value = v
        return v

    def _assert_attrs(self, values):
        if frozenset(values.keys()) != self.__TOP_ATTRS:
            raise ValueError(f"incorrect top level attrs={sorted(values.keys())}")
        #TODO(robnagler) verify other fields are valid (nullable, etc.)
        if values.name is None:
            raise ValueError("no field name")
        return values


class Button(Base):
    def _defaults(self, *overrides):
        return super()._defaults(
            PKDict(
                name="Button",
                ui=PKDict(widget="button"),
                # value is always None
                value=None,
            ),
            *overrides,
        )

    def _from_literal(self, value):
        if value is None:
            return None
        return InvalidFieldValue("not None")


class Enum(Base):
    def _defaults(self, *overrides):
        return super()._defaults(
            PKDict(
                constraints=PKDict(choices=PKDict()),
                name="Enum",
                ui=PKDict(widget="select"),
            ),
            *overrides,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__choice_values = xx

    def _assert_attrs(self, values):
        def _convert(pairs):
            t = None
            for k, v in pairs:
                if k is None:
                    raise ValueError("choice label may not be None value={v}")
                k = str(k)
                if v is None:
                    raise ValueError("choice value may not be None label={k}")
                if not isinstance(v, (int, str)):
                    raise ValueError("invalid choice value type={type(v)} label={k}")
                if t is None:
                    t = type(v)
                elif t != type(v):
                    t = False
                if isinstance(t, int):







        def _iter(choices):
            if isinstance(rv.constraints.choices, dict):
                return choices.items()
            if isinstance(rv.constraints.choices, (list, tuple, set)):
                return (k, k) for k in choices
            raise ValueError(f"invalid choices type={type(choices)}")

        rv = super()._assert_attrs(values)
        rv.constraints.choices = PKDict(
            _convert(_iter(rv.constraints.choices)),
        )




    def _from_literal(self, value):
        try:
            if (rv := self.__choices.get(str(value).lower())) is not None:
                return rv
            return InvalidFieldValue(
                "unknown choice",
                choices=tuple(self.__choices.keys()),
            )
        except Exception as e:
            return InvalidFieldValue("incompatible with str", exc=e)


class Float(Base):
    def _defaults(self, *overrides):
        return super()._defaults(
            PKDict(
                name="Float",
                ui=PKDict(widget="float"),
            ),
            *overrides,
        )

    def _from_literal(self, value):
        try:
            return float(value)
        except Exception as e:
            return InvalidFieldValue("not float", exc=e)


class Integer(Base):
    def _defaults(self, *overrides):
        return super()._defaults(
            PKDict(
                name="Integer",
                ui=PKDict(widget="integer"),
            ),
            *overrides,
        )

    def _from_literal(self, value):
        try:
            return int(value)
        except Exception as e:
            return InvalidFieldValue("not integer", exc=e)


class Plot(Base):
    def _defaults(self, *overrides):
        return super()._defaults(
            PKDict(
                name="Plot",
                ui=PKDict(widget="plot"),
            ),
            *overrides,
        )

    def _from_literal(self, value):
        try:
            #TODO(robnagler) validate
            return value
        except Exception as e:
            return InvalidFieldValue("not plot", exc=e)


class String(Base):
    def _defaults(self, *overrides):
        return super()._defaults(
            PKDict(
                name="String",
                ui=PKDict(widget="string"),
            ),
            *overrides,
        )

    def _from_literal(self, value):
        try:
            return str(value)
        except Exception as e:
            return InvalidFieldValue("not string", exc=e)
