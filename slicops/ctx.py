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

    def __init__(self, name):
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
                pykern.pkresource.file_path("sliclet"),
                glob=f"{name}*",
            )
            _check_raw(r)
            k = "ctx"
            self.__fields = _Parser(r, name).fields
            k = "ui_layout"
            self.__ui_layout = slicops.ui_layout.UILayout(r[k], self)
        except Exception as e:
            # TODO(robnagler) eventually use add_note
            if x := getattr(e, "args", None):
                x = ()
            e.args = x + (f"parsing {k} for sliclet={name}",)
            raise e


class _Parser:
    def __init__(self, raw, sliclet):

        def _one(name, attrs, base):
            if not base:
                raise ValueError(f"expecting a base for field={name}")
            if not (b := self.bases.get(base)):
                _sort()
                if not (b := self.fields.get(base)):
                    raise ValueError(
                        f"unknown base={b} or field bases are a cycle field={name}"
                    )
            self.fields[name] = b.new(v)

        def _sort():
            for k, v in tuple(raw.items()):
                del raw[k]
                if not isinstance(v, dict) or not v:
                    raise ValueError(f"expecting a non-empty dict for field={k}")
                # field.Base doesn't know about "base"
                _one(k, v, v.pkdel("base"))

        if not isinstance(raw, dict) or not raw:
            raise ValueError("expecting a non-empty dict")
        self.fields = PKDict()
        self.bases = slicops.field.base_classes()
