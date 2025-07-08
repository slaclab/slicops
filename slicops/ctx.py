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

    def __init__(self, name, path=None):
        def _check_raw(got):
            if not isinstance(got, dict):
                raise ValueError(f"expecting a dict, not type={type(got)}")
            g = set(got.keys())
            if x := g - self.__TOP_KEYS:
                raise ValueError(f"unexpected keys={x}")
            if x := self.__TOP_KEYS - g:
                raise ValueError(f"missing keys={x}")

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
    def __init__(self, ctx, first_time=False):
        self.__ctx = ctx
        self.__updates = PKDict()
        self.__first_time = first_time

    def commit(self, update):

        def _pairs(updates):
            for k, v in updates.items():
                yield k, v.as_dict()

        c = self.__ctx
        u = self.__updates
        self.__ctx = self.__updates = None
        if u:
            # could technically do collision checking on the update
            c.fields.update(u)
            u = PKDict(fields=PKDict(_pairs(u)))
        if self.__first_time:
            u = c.as_dict()
        # TODO(robnagler) only send changes and protect large data being sent
        # screen protects against this by clearing plot when irrelevant
        if u:
            update(u)

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

    def field_set_via_api(self, name, value):
        try:
            o = self.__field(name)
            if not o.ui_get("writable"):
                raise pykern.util.APIError(
                    "field={} is not writable value={}", name, value
                )
            n = self.__field_update(name, o, PKDict(value=value))
            rv = PKDict(field_name=name, value=n.value_get(), old_value=o.value_get())
            # TODO(robnagler) optimize, similar to field_set
            return rv.pkupdate(changed=rv.value != rv.old_value)
        except Exception as e:
            if isinstance(e, pykern.util.APIError):
                raise
            raise pykern.util.APIError("invalid value for field={} error={}", name, e)

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

    def ui_get(self, field, attr):
        return self.__ctx.fields[field].ui_get(attr)

    def __field(self, name):
        if rv := self.__updates.get(name):
            return rv
        return self.__ctx.fields[name]

    def __field_update(self, name, field, overrides):
        rv = self.__updates[name] = field.renew(copy.deepcopy(overrides))
        return rv
