"""Ctx Value

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern import pkconfig, pkresource, pkyaml
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import copy
import re

_PROTOTYPES = None


def prototypes():
    return _PROTOTYPES


class InvalidFieldValue:
    def __init__(self, msg, **kwargs):
        self.msg = msg
        self.kwargs = PKDict(kwargs)

    def __str__(self):
        def _values():
            for k in sorted(self.kwargs.keys()):
                try:
                    yield f"{k}={str(self.kwargs[k]):.100}"
                except:
                    # TODO(robnagler) may be not the best
                    pass

        try:
            return str(self.msg) + " " + " ".join(_values())
        except:
            return super().__str__()


class Base:
    __SIMPLE_TOP_ATTRS = frozenset(("name", "value"))
    __TOP_ATTRS = __SIMPLE_TOP_ATTRS.union(("constraints", "ui"))
    # Others that convert from yaml
    __INVALID_NAMES = frozenset(("true", "false", "null", "none"))
    __VALID_NAME = re.compile("^[a-z]\w+$")

    def __init__(self, prototype, overrides):
        def _copy():
            if prototype is None:
                return self._defaults()
            return copy.deepcopy(prototype._attrs)

        self._attrs = self.__merge(_copy(), overrides)
        self._assert_attrs()
        v = self.value_check(self._attrs.value)
        if isinstance(v, InvalidFieldValue):
            raise ValueError(v)
        self._attrs.value = v

    def new(self, overrides):
        return self.__class__(self, overrides)

    def ui_get(self, name):
        return self._attrs.ui[name]

    def value_check(self, value):
        if value is None or hasattr(value, "__len__") and len(value) == 0:
            if self._attrs.constraints.nullable:
                return None
            rv = InvalidValue(msg="None")
        else:
            v = self._from_literal(value)
            if not isinstance(v, InvalidFieldValue):
                return v
            rv = v
        rv.kwargs.field_name = self._attrs.name
        return v

    def value_get(self):
        return self._attrs.value

    def value_set(self, value):
        v = self.value_check(value)
        if isinstance(v, InvalidFieldValue):
            raise ValueError(str(v))
        self._attrs.value = v
        return v

    def _assert_attrs(self):
        def _check_name(name):
            if not name:
                raise ValueError(f"no field name attrs={self._attrs}")
            n = name.lower()
            if not self.__VALID_NAME.search(n):
                raise ValueError(
                    f"field name={name} must an identifier starting with a letter"
                )
            if n in self.__INVALID_NAMES:
                raise ValueError(
                    f"field name={name} must not be {sorted(self.__INVALID_NAMES)}"
                )
            if n in _PROTOTYPES_LOWER:
                raise ValueError(f"field name={name} may not match builtin prototypes")

        a = self._attrs
        if frozenset(a.keys()) != self.__TOP_ATTRS:
            raise ValueError(f"incorrect top level attrs={sorted(a.keys())}")
        # TODO(robnagler) verify other attrs are valid (nullable, etc.) and ui.label/widget
        _check_name(a.name)

    def _defaults(self, *overrides):
        rv = PKDict(
            constraints=PKDict(max=None, min=None, nullable=True),
            name=None,
            ui=PKDict(label=None, widget=None, writable=True),
            value=None,
        )
        for o in overrides:
            self.__merge(rv, o)
        return rv

    def __merge(self, result, overrides):
        def _update(attr, new):
            # ok if empty
            for k, v in new.items():
                if v is None:
                    attr.pkdel(k)
                else:
                    attr[k] = v

        for t in self.__TOP_ATTRS:
            if (o := overrides.pkdel(t)) is None:
                continue
            if t in self.__SIMPLE_TOP_ATTRS:
                result[t] = o
            elif not isinstance(o, dict):
                raise ValueError(f"overrides {t} is not a dict type={type(o)}")
            else:
                _update(result[t], o)
        if overrides:
            raise ValueError(
                f"unexpected top key(s)={sorted(overrides.keys())}; must be {sorted(self.__TOP_ATTRS)}"
            )
        return result

    def __str__(self):
        try:
            if a := getattr(self, "_attrs", None):
                rv = f"{self.__class__.__name__}("
                if n := a.get("name"):
                    rv += f"{n}={a.get('value')}"
                return rv + ")"
        except:
            pass
        return super().__str__()


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
    __INITIAL_CHOICES = object()

    def _defaults(self, *overrides):
        return super()._defaults(
            PKDict(
                constraints=PKDict(choices=self.__INITIAL_CHOICES),
                name="Enum",
                ui=PKDict(widget="select"),
            ),
            *overrides,
        )

    def _assert_attrs(self):
        def _choices(constraints):
            # Enum._defaults has no choices
            c = constraints.choices
            constraints.choices = rv = PKDict(
                () if c is self.__INITIAL_CHOICES else _convert(tuple(_pairs(c)))
            )
            return rv

        def _convert(pairs):
            t = _type(pairs)
            s = set()
            for k, v in pairs:
                yield str(k), t(v)

        def _pairs(values):
            if isinstance(values, dict):
                return values.items()
            if isinstance(values, (list, tuple, set)):
                return ((k, k) for k in values)
            raise ValueError(f"invalid choices type={type(values)}")

        def _type(pairs):
            t = None
            for k, v in pairs:
                if k is None:
                    raise ValueError(f"choice label may not be None value={v}")
                if v is None:
                    raise ValueError(f"choice value may not be None label={k}")
                if not isinstance(v, (int, str)):
                    raise ValueError(f"invalid choice value type={type(v)} label={k}")
                if t is None:
                    t = type(v)
                elif t != type(v):
                    return str
            if t is None:
                raise ValueError("must have at least one choice")
            return t

        super()._assert_attrs()
        self.__map = self.__create_map(_choices(self._attrs.constraints))
        # validate and raise
        self.value_set(self._attrs.value)

    def __create_map(self, choices):
        def _cross_check(labels, values):
            for k, v in labels.items():
                if (x := values.get(k)) is not None and x != v:
                    raise ValueError(
                        f"choice labels and values must reverse map with lower label={k} maps to {v} and {x}"
                    )
            return labels.pkupdate(values)

        def _duplicates(kind):
            rv = PKDict(_iter(kind))
            if len(rv) != len(choices):
                raise ValueError(
                    f"duplicate choice {kind} (case insensitive) choices={choices}"
                )
            return rv

        def _iter(kind):
            for k, v in choices.items():
                yield _lower((v if kind == "value" else k), kind), v

        def _lower(value, kind):
            rv = str(value).lower()
            if len(rv) == 0:
                raise ValueError(f"choice {kind} may not be a zero length string")
            return rv

        return _cross_check(_duplicates("label"), _duplicates("value"))

    def _from_literal(self, value):
        try:
            if (rv := self.__map.get(str(value).lower())) is not None:
                return rv
            return InvalidFieldValue(
                "unknown choice",
                value=value,
                choices=tuple(self.__map.keys()),
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
        # TODO(robnaler) need to verify attributes
        return super()._defaults(
            PKDict(
                name="Plot",
                ui=PKDict(widget="plot"),
            ),
            *overrides,
        )

    def _from_literal(self, value):
        try:
            # TODO(robnagler) validate
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


def _init():
    global _PROTOTYPES, _PROTOTYPES_LOWER

    def _gen():
        for c in (Button, Enum, Float, Integer, Plot, String):
            yield c.__name__, c(None, PKDict())

    # needed in Base.__init__
    _PROTOTYPES_LOWER = frozenset()
    _PROTOTYPES = PKDict(_gen())
    _PROTOTYPES_LOWER = frozenset(c.lower() for c in _PROTOTYPES)


_init()
