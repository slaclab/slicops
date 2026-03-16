"""Hello World Sliclet

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import slicops.sliclet
from pykern.pkcollections import PKDict


_MESSAGE = PKDict(Bye = "Ta Ta!", Hello = "Hello World!")
_LABEL_FLIP = PKDict(Bye = "Hello", Hello = "Bye")

class Hello(slicops.sliclet.Base):
    def on_click_bye(self, txn, **kwargs):
        txn.field_value_set("message", "Ta Ta!")

    def on_click_greeting(self, txn, **kwargs):
        x = txn.group_attr("greeting.ui.label")
        txn.field_value_set("message", _MESSAGE[x])
        txn.group_attr_set("greeting.ui.label", _LABEL_FLIP[x])

CLASS = Hello
