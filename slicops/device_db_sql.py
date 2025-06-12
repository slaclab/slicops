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
        uri=pykern.sql_db.sqlite_uri(_path())
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
            device_attr=PKDict(
                device_attr_id=p + " 6",
                device_attr_name=n,
                device_attr_value=s,
            ),
        ),
    )

def insert(device_decl, session):
    tables = insert.tables(as_dict=True)

    def _area(name):
        session.insert()
    _area_id(device_decl.area)
                        "area": "UNDS",
                        "beam_path": (
                            "CU_SXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",

                        "area": "UNDS",
                        "beam_path": (
                            "CU_SXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 3661.222,
                        "device_name": "BOD10",
                        "pv_prefix": "YAGS:UNDS:3575",
    for a in device_decl.accessor.values():
        _areas(a)

                        "accessor": PKDict(
                            {
                                "acquire": PKDict(
                                    {
                                        "name": "acquire",
                                        "pv_base": "Acquire",
                                        "pv_name": "YAGS:UNDS:3575:Acquire",
                                        "pv_writable": True,
                                        "py_type": "bool",
                                    }
                                ),
                                "bit_depth": PKDict(
                                    {
                                        "name": "bit_depth",
                                        "pv_base": "N_OF_BITS",
                                        "pv_name": "YAGS:UNDS:3575:N_OF_BITS",
                                        "py_type": "int",
                                    }
                                ),
                                "image": PKDict(
                                    {
                                        "array_is_row_major": True,
                                        "name": "image",
                                        "pv_base": "Image:ArrayData",
                                        "pv_name": "YAGS:UNDS:3575:Image:ArrayData",
                                        "py_type": "ndarray",
                                    }
                                ),
                                "num_cols": PKDict(
                                    {
                                        "name": "num_cols",
                                        "pv_base": "Image:ArraySize1_RBV",
                                        "pv_name": "YAGS:UNDS:3575:Image:ArraySize1_RBV",
                                        "py_type": "int",
                                    }
                                ),
                                "num_rows": PKDict(
                                    {
                                        "name": "num_rows",
                                        "pv_base": "Image:ArraySize0_RBV",
                                        "pv_name": "YAGS:UNDS:3575:Image:ArraySize0_RBV",
                                        "py_type": "int",
                                    }
                                ),
                            }
                        ),
                        "area": "UNDS",
                        "beam_path": (
                            "CU_SXR",
                            "SC_S2_X",
                            "SC_SFTS",
                            "SC_STMO",
                            "SC_STXI",
                            "SC_SXR",
                        ),
                        "device_kind": "screen",
                        "device_length": 3661.222,
                        "device_name": "BOD10",
                        "pv_prefix": "YAGS:UNDS:3575",
                    }

    pass


def recreate(devices):
    assert not _meta
    pykern.pkio.unchecked_remove(_path)
    _init()
    return _Inserter(devices, _meta).counts


def _path():
    return pykern.pkresource.file_path(_BASE_PATH)


def _Inserter:
    def __init__(self, devices, meta):
        self.counts = PKDict()
        with meta.session() as s:
            self.session = s
            self.tables = meta.tables(as_dict=True)
            self.beam_areas = PKDict(self._beam_areas(devices, tables.beam_area))
        self.counts =

    def _beam_areas(self, devices, table):
        for n in sorted(set(d.area for d in devices)):
            yield n, s.insert(table, beam_area_name=n).beam_area_id
