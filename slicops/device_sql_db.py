"""SQL db of `lcls_tools.common.devices.yaml`

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import pykern.sql_db
import pykern.pkresource

_BASE_PATH = "device_sql_db.sqlite3"

_meta = None


def insert(device_decl, session):
    tables = insert.tables(as_dict=True)
    pass


def recreate(parser):
    assert not _meta
    pykern.pkio.unchecked_remove(_path())
    pkdlog(_path())
    _init()
    return _Inserter(parser, _meta).counts


_METADATA_SKIP = frozenset(
    (
        "area",
        "beam_path",
        "bpms_after_wire",
        "bpms_before_wire",
        "lblms",
        "type",
    ),
)


class _Inserter:
    def __init__(self, parser, meta):
        self.counts = PKDict()
        self.parser = parser
        with meta.session() as s:
            self._beam_paths(s)
            self._devices(s)

    def _beam_paths(self, session):
        for a, paths in self.parser.beam_paths.items():
            session.insert("beam_area", beam_area=a)
            for p in paths:
                session.insert("beam_path", beam_area=a, beam_path=p)

    def _devices(self, session):
        for n, d in self.parser.devices.items():
            session.insert(
                "device",
                device_name=d.name,
                beam_area=d.metadata.area,
                device_type=d.metadata.type,
                pv_prefix=d.pv_prefix,
            )
            for k, v in d.pvs.items():
                session.insert("device_pv", device_name=n, accessor_name=k, pv_suffix=v)
            for k, v in d.metadata.items():
                if k not in _METADATA_SKIP:
                    session.insert(
                        "device_meta_float",
                        device_name=n,
                        device_meta_name=k,
                        device_meta_value=float(v),
                    )


def _path():
    return pykern.pkresource.file_path(".").join(_BASE_PATH)


def _init():
    global _meta
    if _meta is not None:
        return
    s = "str 64"
    p = s + " primary_key"
    n = s + " index"
    # Since created once, no need for created/modified entries
    _meta = pykern.sql_db.Meta(
        uri=pykern.sql_db.sqlite_uri(_path()),
        schema=PKDict(
            beam_area=PKDict(
                beam_area=p,
            ),
            beam_path=PKDict(
                beam_area=p + " foreign",
                beam_path=p,
            ),
            device=PKDict(
                device_name=p,
                beam_area=n + " foreign",
                device_type=n,
                pv_prefix=s,
            ),
            device_pv=PKDict(
                device_name=p + " foreign",
                accessor_name=p,
                pv_suffix=s,
            ),
            device_meta_float=PKDict(
                device_name=p + " foreign",
                device_meta_name=p,
                device_meta_value="float 64",
            ),
        ),
    )
