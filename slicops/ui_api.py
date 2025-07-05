"""UI APIs

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.quest.API
import slicops.sliclet
import pykern.api.util
import pykern.util


def api_classes():
    return (API,)


_UPDATE_Q_KEY = "update_q"
_SLICLET_KEY = "sliclet"


class API(slicops.quest.API):
    """Implementation for the Screen (Profile Monitor) application"""

    async def api_ui_action(self, api_args):
        return await self.session[_SLICLET_KEY].ui_action()

    @pykern.api.util.subscription
    async def api_ui_update(self, api_args):
        if self.session.get(_UPDATE_Q_KEY):
            raise pykern.util.APIError("already updating")
        try:
            q = asyncio.Queue()
            self.session.pkupdate(
                {
                    _SLICLET_KEY: slicops.sliclet.instance(api_args.sliclet, q),
                    _UPDATE_Q_KEY: q,
                }
            )
            while not self.is_quest_end():
                r = await q.get()
                q.task_done()
                if r is None:
                    return None
                if isinstance(r, Exception):
                    raise pykern.util.APIError(r)
                self.subscription.result_put(r)
        finally:
            if "session" in self:
                self.session.pkdel(_UPDATE_Q_KEY)
                self.session.pkdel(_SLICLET_KEY)
