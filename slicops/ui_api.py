"""UI APIs

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.quest.API
import slicops.sliclet
import pykern.api.util


def api_classes():
    return (API,)


_UPDATE_Q_KEY = "update_q"
_SLICLET_KEY = "sliclet"


class API(slicops.quest.API):
    """Implementation for the Screen (Profile Monitor) application"""

    async def api_ui_boot(self, api_args):
        q = self.session[_UPDATE_Q_KEY] = asyncio.Queue()
        s = self.session[_SLICLET_KEY] = slicops.sliclet.instance(api_args.sliclet, q)
        return s.ui_boot()

    async def api_ui_action(self, api_args):
        api_args
        # TODO(robnagler) if accepting ui_ctx, then need to update valid_values here
        return self._return(ux).pkupdate(
            # TODO(pjm): need a better way to load a resource for a sliclet
            layout=pkyaml.load_file(pkresource.file_path("layout/screen.yaml")),
        )

    @pykern.api.util.subscription
    async def api_ui_update(self, api_args):
        if self.session.get(_UPDATE_Q_KEY):
            raise RuntimeError("already updating")
        try:
            q = self.session[_UPDATE_Q_KEY] = asyncio.Queue()
            while not self.is_quest_end():
                r = await q.get()
                q.task_done()
                if r is None:
                    return None
                self.subscription.result_put(r)
        finally:
            if "session" in self:
                self.session.pkdel(_UPDATE_Q_KEY)
