"""parse layout

:copyright: Copyright (c) 2025 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import copy


class UILayout:

    def __init__(self, rows, ctx):
        self._errors = []
        self._path = []
        r = self._recurse("row", rows, True)
        if self._errors:
            raise ValueError("\n".join(self._errors))
        del self["_errors"]
        del self["_path"]
        self.rows = r

    def _error(self, msg):
        def _path():
            for p in self._path:
                rv = p.op
                if p.index is not None:
                    rv += f"[p.index]"
                yield rv

        if v := self._path[-1].value:
            if isinstance(v, dict):
                v = "keys=" + " ".join(v.keys())
            else:
                v = str(v)
            # doesn't need to be too long
            v = " value=" + v[:50]
        else:
            v = ""
        self._errors.append(".".join(_path()) + v + " " + msg)
        return None

    def _op_cell(self, value):
        if not ctx.is_field(value):
            return _error("field not found")
        return PKDict(cell=value)

    def _op_col(self, value):
        if (c := value.pkdel("css")):
            c = self._recurse("css", c)
        else:
            self._error("no css")
        if (r := value.pkdel("rows")):
            r = self._recurse("row", r, True)
        if value:
            self._error("expecting css or rows")
        return PKDict(css=c, rows=r)

    def _op_row(self, value):
        if isinstance(v, str):
            return self._recurse("cell", v)
        if isinstance(v, dict):
            k = tuple(v.keys())
            if len(k) == 1:
                v = value[k[0]]
                if k[0] == "cell_group":
                    return self._recurse("cell", v)
                elif k[0] == "cols":
                    return self._recurse("col", v, True)
            return _self._error("must be cols or cell_group")
        return self._error("must be a field name, cols, or cell_group")

    def _recurse(self, op, value, is_list=False):
        self._path.append(PKDict(op=op, value=value, index=None))
        try:
            o = getattr(self, op)
            if not is_list:
                if not isinstance(value, str):
                    return self._error("must be a string")
                v = " ".join(value.split())
                if len(v) == 0:
                    return self._error("may not be empty")
                return o(v)
            if not isinstance(value, (tuple, list)):
                return self._error("expecting a list")
            if not value:
                return self._error(f"at least one {op}")
            return tuple(o(v) for self._path[-1].index, v in enumerate(value))
        finally:
            self._path.pop()
