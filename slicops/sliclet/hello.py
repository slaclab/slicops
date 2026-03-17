"""Hello World Sliclet

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import slicops.sliclet
import slicops.device


class Hello(slicops.sliclet.Base):

    def handle_destroy(self):
        if self.__device:
            self.__device.destroy()

    def handle_init(self, txn):
        self.__device = None

    def handle_start(self, txn):
        self.__device = slicops.device.Device("DEV_CAMERA")
        self.__device.accessor("acquire").monitor(self.__handle_acquire)

    def __handle_acquire(self, change):
        def _msg():
            if "connected" in change:
                return "Connected"
            if "error" in change:
                return f"Error: {change.error}"
            if change.value:
                return "Acquiring"
            return "Idle"

        with self.lock_for_update() as txn:
            txn.field_value_set("status", _msg())


CLASS = Hello
