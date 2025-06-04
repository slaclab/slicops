"""Common configuration

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import pykern.pkconfig
import pykern.pkasyncio
import pykern.pkunit
import pykern.util

_cfg = None


def cfg():
    """`PKDict` of common configuration.

    db_api
       api_uri, tcp_ip, tcp_port, and vue_port values. `PKDict`
       is compatible with `pykern.api.server.start`,

    Returns:
        PKDict: configuration values. (Make a copy before modifying.)

    """
    global _cfg
    if _cfg:
        return _cfg
    _cfg = pykern.pkconfig.init(
        ui_api=PKDict(
            api_uri=("/api-v1", str, "URI for API requests"),
            tcp_ip=(
                pykern.pkconst.LOCALHOST_IP,
                pykern.pkasyncio.cfg_ip,
                "IP address for server",
            ),
            tcp_port=(8000, pykern.pkasyncio.cfg_port, "port of server"),
            vue_port=(8008, pykern.pkasyncio.cfg_port, "port of Vue dev server"),
        ),
    )
    return _cfg
