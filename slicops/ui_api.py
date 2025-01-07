"""UI API server implementation

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import importlib
import slicops.quest


class UIAPI(slicops.quest.API):
    """API entry points to be dispatched

    All entry points take ``api_args``, which is a dictionary of arguments.

    Entry points return a `PKDict`, but could be an any Python data structure.

    Or, raise a `pykern.quest.APIError`.
    """

    def _app_implementation(self, api_args):
        assert 'app_name' in api_args
        return importlib.import_module(f'slicops.app.{api_args.app_name}').new_implementation(
            PKDict(
                api_args=api_args,
            )
        )

    async def api_action(self, api_args):
        return _app_implementation(api_args).action()

    async def api_echo(self, api_args):
        return self._app_implementation(api_args).api_args.value

    async def api_init_app(self, api_args):
        a = self._app_implementation(api_args)
        return PKDict(
            schema=a.schema(),
            instance=a.default_instance(),
        )
