"""Holds fields and ui_layout

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import copy
import pykern.fconf
import pykern.pkresource
import pykern.util
import slicops.field
import slicops.ui_layout


class Ctx:
    __TOP_KEYS = frozenset(("fields", "ui_layout"))

    def __init__(self, name, title, path=None):
        def _check_raw(got):
            if not isinstance(got, dict):
                raise ValueError(f"expecting a dict, not type={type(got)}")
            g = set(got.keys())
            if x := g - self.__TOP_KEYS:
                raise ValueError(f"unexpected keys={x}")
            if x := self.__TOP_KEYS - g:
                raise ValueError(f"missing keys={x}")

        self.name = name
        self.title = title

        step = "yaml"
        try:
            r = pykern.fconf.parse_all(
                path or pykern.pkresource.file_path("sliclet"),
                glob=f"{name}*",
            )
            _check_raw(r)
            step = "fields"
            self.fields = self.__parse(r[step], PKDict(), slicops.field.prototypes())
            step = "ui_layout"
            self.ui_layout = slicops.ui_layout.UILayout(r[step], self)
        except Exception as e:
            # TODO(robnagler) eventually use add_note
            if not (x := getattr(e, "args", None)):
                x = ()
            e.args = x + (f"parsing {step} for sliclet={name}",)
            raise e

    def as_dict(self):
        return PKDict(
            fields=PKDict((k, v.as_dict()) for k, v in self.fields.items()),
            ui_layout=PKDict(rows=copy.deepcopy(self.ui_layout.rows)),
        )

    def first_time(self):
        u = self.as_dict()
        u.sliclet_title = self.title
        u.sliclet_name = self.name
        return u

    def __parse(self, raw, fields, prototypes):

        def _one(name, attrs, prototype):
            if not prototype:
                raise ValueError(f"expecting a prototype for field={name}")
            if not (b := prototypes.get(prototype)):
                _sort()
                if not (b := fields.get(prototype)):
                    raise ValueError(
                        f"unknown prototype={prototype} or prototypes are a cycle field={name}"
                    )
            attrs.name = name
            fields[name] = b.new(attrs)

        def _sort():
            for k, v in tuple(raw.items()):
                if k not in raw:
                    # recursion already handled
                    continue
                del raw[k]
                if not isinstance(v, dict) or not v:
                    raise ValueError(f"expecting a non-empty dict for field={k}")
                # field.Base doesn't know about "prototype"
                _one(k, v, v.pkdel("prototype"))

        if not isinstance(raw, dict) or not raw:
            raise ValueError("expecting a non-empty dict")
        _sort()
        return fields


class Txn:
    def __init__(self, ctx):
        self.__ctx = ctx
        self.__updates = PKDict()

    def commit(self, update):

        def _pairs(updates):
            for k, v in updates.items():
                yield k, v.as_dict()

        c = self.__ctx
        u = self.__updates
        self.__ctx = self.__updates = None
        if not u:
            return
        # could technically do collision checking on the update
        c.fields.update(u)
        # TODO(robnagler) only send changes and protect large data being sent
        # screen protects against this by clearing plot when irrelevant
        if update:
            update(PKDict(fields=PKDict(_pairs(u))))

    def is_field_value_valid(self, name, value):
        return not isinstance(
            self.__field(name).value_check(value), slicops.field.InvalidFieldValue
        )

    def field_get(self, name):
        return self.__field(name).value_get()

    def field_names(self):
        # keys are always the same
        return tuple(self.__ctx.fields.keys())

    def field_set(self, name, value):
        # TODO(robnagler) optimize this case to not validate constraints/ui
        #   could possibly optimize the ui and constraints parts when a copy
        #   vs new with _defaults() (which should get validated first time)
        self.__field_update(name, self.__field(name), PKDict(value=value))

    def field_set_via_api(self, name, value, on_method):
        def _update(old, new):
            rv = PKDict(field_name=name, on_method=on_method, txn=self)
            if on_method.kind == "click":
                if new.group_get("ui", "clickable"):
                    return rv
                pkdlog("on_click_{} exists and clickable=False", c.field_name)
                return None
            if on_method.kind == "change":
                rv.pkupdate(value=n.value_get(), old_value=o.value_get())
                if rv.value == rv.old_value:
                    return None
                return rv
            raise AssertionError(
                f"invalid no_method.kind={on_method.kind} field={name}"
            )

        try:
            o = self.__field(name)
            if not o.group_get("ui", "writable"):
                raise pykern.util.APIError(
                    "field={} is not writable value={}", name, value
                )
            n = self.__field_update(name, o, PKDict(value=value))
            return _update(o, n) if on_method else None
        except Exception as e:
            if isinstance(e, pykern.util.APIError):
                raise
            raise pykern.util.APIError("invalid value for field={} error={}", name, e)

    def group_get(self, field, group, attr=None):
        return self.__ctx.fields[field].group_get(group, attr)

    def multi_set(self, *args):
        def _args():
            if len(args) > 1:
                return args
            if len(args) == 0:
                raise AssetionError("must be at list one update")
            if isinstance(args[0][0], str):
                # (("a", 1))
                return args
            # ((("a", 1), ("b", 2), ..)) or a dict
            return args[0]

        def _parse():
            rv = PKDict()
            for k, v in _args():
                rv.pknested_set(k, v)
            return rv

        for k, v in _parse().items():
            self.__field_update(k, self.__field(k), v)

    def rollback(self):
        self.__ctx = self.__updates = None

    def __field(self, name):
        if rv := self.__updates.get(name):
            return rv
        return self.__ctx.fields[name]

    def __field_update(self, name, field, overrides):
        rv = self.__updates[name] = field.renew(copy.deepcopy(overrides))
        return rv
