"""Hello World Sliclet

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import slicops.sliclet

_MESSAGE = {"Bye": "Ta Ta!", "Hello": "Hello World!"}
_LABEL_FLIP = {"Bye": "Hello", "Hello": "Bye"}

class Hello(slicops.sliclet.Base):

    def on_click_greeting(self, txn, **kwargs):

        def _n_col():
            if not hasattr(self, "__device"):
                self.__device = slicops.device.Device("DEV_CAMERA")
            return self.__device.accessor("n_col").get()
        
        x = txn.group_attr("greeting.ui.label")
        txn.field_value_set("message", _MESSAGE[x])
        txn.group_attr_set("greeting.ui.label", _LABEL_FLIP[x])

CLASS = Hello
