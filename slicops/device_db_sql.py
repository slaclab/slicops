"""SQL db of `lcls_tools.common.devices.yaml`

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import pykern.sql_db
import pykern.pkresource

_BASE_PATH = "devices.sqlite3"

_meta = None

def _init():
    global _meta
    if _meta is not None:
        return
    s = "str 64"
    p = "primary_id"
    n = s + " index"
    # Since created once, no need for created/modified entries
    _meta = sql_db.Meta(
        uri=pykern.sql_db.sqlite_uri(pykern.pkresource.file_path(_BASE_PATH)),
        schema=PKDict(
            beam_area=PKDict(
                beam_area_id=p + " 1",
                beam_area_name=n,
            ),
            beam_path=PKDict(
                beam_path_id=p + " 2",
                beam_area_id=p,
                beam_path_name=n,
            ),
            device_kind=PKDict(
                device_kind_id=p + " 3",
                device_kind_name=n,
                # characteristics?
            ),
            device=PKDict(
                device_id=p + " 4",
                device_name=n,
                beam_area_id=p,
                device_kind_id=p,
                device_length="float 64",
                pv_prefix=s,
                # If null, then isn't an image. Maybe not the way to specify?
                array_is_row_major="bool nullable",
            ),
            device_pv=PKDict(
                device_pv_id=p + " 5",
                device_id=p,
                accessor_name=s,
                # TODO(robnagler) may not want these indexed
                pv_base=n,
                pv_name=n,
                pv_writable="bool",
                py_type=s,
            ),
        ),
    )
