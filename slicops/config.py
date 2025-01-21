"""Common configuration

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import pykern.pkasyncio
import pykern.pkconfig
import pykern.pkunit
import pykern.util

_cfg = None


def cfg():
    """`PKDict` of common configuration.

    db_api
       api_uri, auth_secret, tcp_ip, and tcp_port values. `PKDict`
       is compatible with `pykern.http.server_start`,

    Returns:
        PKDict: configuration values. (Make a copy before modifying.)

    """
    return _cfg


def dev_path(path, **ensure_kwargs):
    """Prefixes root of the directory for development to `path`.

    Returns:
        py.path: absolute path with parent directories created
    """
    return _dev_root_d.join(path)


def _init():
    global _cfg
    if _cfg:
        return
    if pykern.pkconfig.channel_in("dev"):
        global _dev_root_d

        _dev_root_d = pykern.util.dev_run_dir(dev_path)
    _cfg = pykern.pkconfig.init(
        ui_api=PKDict(
            api_uri=("/api-v1", str, "URI for API requests"),
            tcp_ip=(None, pykern.pkasyncio.cfg_ip, "IP address for server"),
            tcp_port=(9030, pykern.pkasyncio.cfg_ip, "port of server"),
        ),
    )


_init()
