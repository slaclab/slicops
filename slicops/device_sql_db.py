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


def insert(device_decl, session):
    tables = insert.tables(as_dict=True)
    pass


def recreate(devices):
    assert not _meta
    pykern.pkio.unchecked_remove(_path)
    _init()
    return _Inserter(devices, _meta).counts


class _Inserter:
    def __init__(self, devices, meta):
        self.counts = PKDict()
        with meta.session() as s:
            self.session = s
            self.tables = meta.tables(as_dict=True)
            self.beam_areas = PKDict(self._beam_areas(devices, tables.beam_area))

    def _beam_areas(self, devices, table):
        # m.pkdel(bpms_after_wire",
        #  "bpms_before_wire",


        for n in sorted(set(d.area for d in devices)):
            yield n, s.insert(table, beam_area_name=n).beam_area_id


def _path():
    return pykern.pkresource.file_path(_BASE_PATH)


def _init():
    global _meta
    if _meta is not None:
        return
    s = "str 64"
    p = s + " primary_key"
    n = s + " index"
    # Since created once, no need for created/modified entries
    _meta = sql_db.Meta(
        uri=pykern.sql_db.sqlite_uri(_path()),
        schema=PKDict(
            beam_path=PKDict(
                beam_area=p,
                beam_path_name=p,
            ),
            device=PKDict(
                device_name=p,
                beam_area=n,
                device_kind=n,
                device_type=n,
                pv_prefix=s,
            ),
            device_pv=PKDict(
                device_name=p + " foreign",
                accessor_name=p,
                pv_suffix=s,
            ),
            device_meta_float=PKDict(
                device_name=p + "foreign",
                device_meta_name=p,
                device_meta_value="float",
            ),
        ),
    )
