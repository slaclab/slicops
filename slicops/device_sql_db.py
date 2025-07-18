"""SQL db of `lcls_tools.common.devices.yaml`.

Use slicops.device_db for a stable interface.

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import pykern.sql_db
import pykern.pkresource
import sqlalchemy

_BASE_PATH = "device_db.sqlite3"

_meta = None


def beam_paths():
    with _session() as s:
        c = s.t.beam_path.c.beam_path
        return tuple(
            r.beam_path for r in s.select(sqlalchemy.select(c).distinct().order_by(c))
        )


def device(name):
    with _session() as s:
        return PKDict(s.select_one("device", PKDict(device_name=name))).pkupdate(
            accessor=PKDict(
                {
                    r.accessor_name: PKDict(r)
                    for r in s.select("device_pv", PKDict(device_name=name))
                }
            ),
        )


def device_names(device_type, beam_path):
    with _session() as s:
        c = s.t.device.c.device_name
        return tuple(
            r.device_name
            for r in s.select(
                sqlalchemy.select(c)
                .join(
                    s.t.beam_path,
                    s.t.beam_path.c.beam_area == s.t.device.c.beam_area,
                )
                .where(
                    s.t.beam_path.c.beam_path == beam_path,
                    s.t.device.c.device_type == device_type,
                )
                .order_by(c)
            )
        )


def upstream_devices(device_type, accessor_name, beam_path, device_name):
    with _session() as s:
        # select device.device_name from device_meta_float, device where device_meta_name = 'sum_l_meters' and device_meta_value < 33 and device.device_type = 'PROF' and device.device_name = device_meta_float.device_name;
        c = s.t.device_meta_float.c.device_name
        _assert_on_beampath(device_name, beam_path, s)
        return tuple(
            r.device_name
            for r in s.select(
                sqlalchemy.select(c)
                .select_from(
                    s.t.device_meta_float.join(
                        s.t.device,
                        s.t.device.c.device_name == c,
                    ).join(
                        s.t.beam_path,
                        s.t.beam_path.c.beam_area == s.t.device.c.beam_area,
                    ).join(
                        s.t.device_pv,
                        s.t.device_pv.c.device_name == c,
                    )
                )
                .where(
                    s.t.beam_path.c.beam_path == beam_path,
                    s.t.device_meta_float.c.device_meta_name == "sum_l_meters",
                    s.t.device_meta_float.c.device_meta_value
                    < _device_meta(device_name, "sum_l_meters", s),
                    s.t.device.c.device_type == device_type,
                    s.t.device_pv.c.accessor_name == accessor_name,
                )
                .order_by(s.t.device_meta_float.c.device_meta_value)
            )
        )

def _assert_on_beampath(device, beam_path, s):
    c = s.t.device.c.device_name
    v = s.select_one_or_none(
        sqlalchemy.select(c)
        .select_from(
            s.t.device.join(
                s.t.beam_path,
                s.t.beam_path.c.beam_area == s.t.device.c.beam_area,
            )
        ).where(
            s.t.device.c.device_name == device,
            s.t.beam_path.c.beam_path == beam_path,
        ),
        None
    )
    if v is None:
        raise ValueError(f"device={device} is not in beam_path={beam_path}")

def _device_meta(device, meta, s):
    return s.select_one(
        "device_meta_float", PKDict(device_name=device, device_meta_name=meta)
    ).device_meta_value


def recreate(parser):
    """Recreates db"""
    assert not _meta
    # Don't remove unless we have valid data
    assert parser.devices
    pykern.pkio.unchecked_remove(_path())
    pkdlog(_path())
    return _Inserter(parser).counts


class _Inserter:
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

    def __init__(self, parser):
        self.counts = PKDict(beam_areas=0, beam_paths=0, devices=0)
        self.parser = parser
        with _session() as s:
            self._beam_paths(s)
            self._devices(s)

    def _beam_paths(self, session):
        for a, paths in self.parser.beam_paths.items():
            self.counts.beam_areas += 1
            session.insert("beam_area", beam_area=a)
            for p in paths:
                self.counts.beam_paths += 1
                session.insert("beam_path", beam_area=a, beam_path=p)

    def _devices(self, session):
        for n, d in self.parser.devices.items():
            self.counts.devices += 1
            session.insert(
                "device",
                device_name=d.name,
                beam_area=d.metadata.area,
                device_type=d.metadata.type,
                pv_prefix=d.pv_prefix,
            )
            for k, v in d.pvs.items():
                session.insert("device_pv", device_name=n, accessor_name=k, pv_name=v)
            for k, v in d.metadata.items():
                if k not in self._METADATA_SKIP:
                    session.insert(
                        "device_meta_float",
                        device_name=n,
                        device_meta_name=k,
                        device_meta_value=float(v),
                    )


def _init():
    global _meta
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
                pv_name=s,
            ),
            device_meta_float=PKDict(
                device_name=p + " foreign",
                device_meta_name=p,
                device_meta_value="float 64",
            ),
        ),
    )


def _path():
    return pykern.pkresource.file_path(".").join(_BASE_PATH)


def _session():
    if _meta is None:
        _init()
    return _meta.session()
