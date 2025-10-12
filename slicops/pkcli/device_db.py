"""Interact with device_db

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import slicops.device_db


def query(func_name, *args):
    """Call func_name in `slicops.device_db`

    Args:
        func_name (str): valid function
        args (str): passed verbatim to function
    Returns:
        object: result of function
    """
    return getattr(slicops.device_db, func_name)(*args)
