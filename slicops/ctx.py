"""Holds Fields and Layout

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import pykern.fconf
import pykern.pkresource
import slicops.field
import slicops.ui_layout


class Ctx:
    __TOP_KEYS = frozenset(("ctx", "ui_layout"))

    def __init__(self, name, path=None):
        def _check_raw(got):
            if not isinstance(got, dict):
                raise ValueError(f"expecting a dict, not type={type(got)}")
            g = set(got.keys())
            if x := g - self.__TOP_KEYS:
                raise ValueError(f"unexpected keys={x}")
            if x := self.__TOP_KEYS - g:
                raise ValueError(f"missing keys={x}")

        k = "yaml"
        try:
            r = pykern.fconf.parse_all(
                path or pykern.pkresource.file_path("sliclet"),
                glob=f"{name}*",
            )
            _check_raw(r)
            k = "ctx"
            self._fields = self.__parse(r[k], PKDict(), slicops.field.prototypes())
            k = "ui_layout"
            self._ui_layout = slicops.ui_layout.UILayout(r[k], self)
        except Exception as e:
            # TODO(robnagler) eventually use add_note
            if not (x := getattr(e, "args", None)):
                x = ()
            e.args = x + (f"parsing {k} for sliclet={name}",)
            raise e

    def is_field(self, name):
        return name in self._fields

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
