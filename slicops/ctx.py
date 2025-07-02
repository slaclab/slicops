"""Holds Fields and Layout

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import pykern.fconf
import pykern.pkresource


class Ctx:
    def __init__(self, name):
        # a field becomes a field_class which can be used
        # it would be something field.increment to reference the type
        # field cannot be a module but that would be checked
        self.__fields = self.__init(
            pykern.fconf.parse_all(
                pykern.pkresource.file_path("sliclet/{name}")
            ),
        )

    def ctx_put(self, name, value):
        assert name in self.fields
        self.fields[name] = value

    def ui_boot(self):
        return PKDict(ui_ctx=PKDict(), layout=self._raw.layout)

    def __init(self, raw):
        # need to deal with relationships, must be DAG
