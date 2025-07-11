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
    __GROUP_ATTRS = frozenset(("constraints", "links", "ui"))
    __TOP_ATTRS = __SIMPLE_TOP_ATTRS.union(__GROUP_ATTRS)
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
        # Validate the value now that constaints are checked
        self.value_set(self._attrs.value)

    def as_dict(self):
        return PKDict((k, copy.deepcopy(self._attrs[k])) for k in self.__TOP_ATTRS)

    def group_get(self, group, attr=None):
        if group not in self.__GROUP_ATTRS:
            raise AssertionError(f"invalid group={group} must be {self.__GROUP_ATTRS}")
        g = self._attrs[group]
        return g.copy() if attr is None else g[attr]

    def new(self, overrides):
        # New instances do not inherit labels
        l = overrides.pkunchecked_nested_get("ui.label")
        rv = self.__class__(self, overrides)
        if not l:
            rv._attrs.ui.label = rv._attrs.name.replace("_", " ").title()
        return rv

    def renew(self, overrides):
        # Updating an instance inherits everything
        return self.__class__(self, overrides)

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
        return rv

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

    def _check_min_max(self, value):
        if (m := self._attrs.constraints.min) is not None and value < m:
            return InvalidFieldValue(f"less than min={m}")
        if (m := self._attrs.constraints.max) is not None and value > m:
            return InvalidFieldValue(f"greater than max={m}")
        return value

    def _defaults(self, *overrides):
        rv = PKDict(
            constraints=PKDict(max=None, min=None, nullable=True),
            links=PKDict(),
            name=None,
            ui=PKDict(
                clickable=False,
                css_kind=None,
                enabled=True,
                label=None,
                visible=True,
                widget=None,
                writable=True,
            ),
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
            if t not in overrides:
                continue
            o = overrides.pkdel(t)
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


class Boolean(Base):
    def _defaults(self, *overrides):
        return super()._defaults(
            PKDict(
                name="Boolean",
                ui=PKDict(
                    widget="toggle",
                    toggle_labels=["Off", "On"],
                ),
            ),
            *overrides,
        )

    def _from_literal(self, value):
        try:
            return bool(value)
        except Exception as e:
            return InvalidFieldValue("not boolean", exc=e)


class Button(Base):
    def _defaults(self, *overrides):
        return super()._defaults(
            PKDict(
                name="Button",
                ui=PKDict(widget="button", clickable=True),
                # value is always None
                value=None,
            ),
            *overrides,
        )

    def _from_literal(self, value):
        if value is None:
            return None
        return InvalidFieldValue("not None")


class Dict(Base):

    def _defaults(self, *overrides):
        # TODO(robnagler) need to verify attributes
        return super()._defaults(
            PKDict(name="Dict"),
            *overrides,
        )

    def _from_literal(self, value):
        try:
            return PKDict(value)
        except Exception as e:
            return InvalidFieldValue("not a dict", exc=e)


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
                # Default to string when no choices
                t = str
            return t

        super()._assert_attrs()
        self.__map = self.__create_map(_choices(self._attrs.constraints))

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
            return self._check_min_max(float(value))
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
            return self._check_min_max(int(value))
        except Exception as e:
            return InvalidFieldValue("not integer", exc=e)


class List(Base):

    def _defaults(self, *overrides):
        # TODO(robnagler) need to verify attributes
        return super()._defaults(
            list(name="List"),
            *overrides,
        )

    def _from_literal(self, value):
        try:
            return list(value)
        except Exception as e:
            return InvalidFieldValue("not a list", exc=e)


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
            v = str(value)
            if isinstance((rv := self._check_min_max(len(v))), InvalidFieldValue):
                return rv
            return v
        except Exception as e:
            return InvalidFieldValue("not string", exc=e)


def _init():
    global _PROTOTYPES, _PROTOTYPES_LOWER

    def _gen():
        for c in (Button, Boolean, Dict, Enum, Float, Integer, String):
            yield c.__name__, c(None, PKDict())

    # needed in Base.__init__
    _PROTOTYPES_LOWER = frozenset()
    _PROTOTYPES = PKDict(_gen())
    _PROTOTYPES_LOWER = frozenset(c.lower() for c in _PROTOTYPES)


_init()
