"""Hello World Sliclet

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import slicops.device
import slicops.sliclet
from slicops.sliclet import PKDict


_MESSAGE = PKDict(Bye="Bye Bye!", Hello="Hello world!")
_LABEL_FLIP = PKDict(Bye="Hello", Hello="Bye")


class Hello(slicops.sliclet.Base):
    def handle_init(self, txn):
        self.__device = None

    def handle_destroy(self):
        self.__device.destroy()

    def on_click_greeting(self, txn, **kwargs):
        def _n_col():
            if self.__device is None:
                self.__device = slicops.device.Device("DEV_CAMERA")
            return self.__device.accessor("n_col").get()

        x = txn.group_attr("greeting", "ui", "label")
        txn.field_value_set(
            "message",
            f"{_MESSAGE[x]} {_n_col()}"
        )
        txn.group_attr_set("greeting.ui.label", _LABEL_FLIP[x])


CLASS = Hello
