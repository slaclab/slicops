"""SQL db of `lcls_tools.common.devices.yaml`.

Use slicops.device_db for a stable interface.

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import numpy
import pykern.pkconfig
import pykern.pkresource
import pykern.sql_db
import slicops.config
import sqlalchemy

_BASE_PATH = "device_db.sqlite3"

_meta = None

_PY_TYPES = PKDict(
    {
        "bool": bool,
        "float": float,
        "int": int,
        "numpy.ndarray": numpy.ndarray,
    }
)


_ACCESSOR_META_DEFAULT = PKDict(
    py_type="float",
    writable=False,
)

_ACCESSOR_META = PKDict(
    acquire=PKDict(py_type="bool", writable=True),
    enabled=PKDict(py_type="int", writable=False),
    image=PKDict(py_type="numpy.ndarray", writable=False),
    n_bits=PKDict(py_type="int", writable=False),
    n_col=PKDict(py_type="int", writable=False),
    n_row=PKDict(py_type="int", writable=False),
    start_scan=PKDict(py_type="int", writable=True),
    target_control=PKDict(py_type="int", writable=True),
    target_status=PKDict(py_type="int", writable=False),
)

def beam_paths():
    with _session() as s:
        c = s.t.beam_path.c.beam_path
        return tuple(
            r.beam_path for r in s.select(sqlalchemy.select(c).distinct().order_by(c))
        )


def device(name):
    def _py_type(rec):
        return rec.pkupdate(py_type=_PY_TYPES[rec.py_type])

    with _session() as s:
        return PKDict(s.select_one("device", PKDict(device_name=name))).pkupdate(
            accessor=PKDict(
                {
                    r.accessor_name: _py_type(PKDict(r))
                    for r in s.select("device_accessor", PKDict(device_name=name))
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


def upstream_devices(device_type, required_accessor, beam_path, end_device):
    with _session() as s:
        # select device.device_name from device_meta_float, device where device_meta_name = 'sum_l_meters' and device_meta_value < 33 and device.device_type = 'PROF' and device.device_name = device_meta_float.device_name;
        c = s.t.device_meta_float.c.device_name
        _assert_on_beampath(end_device, beam_path, s)
        return tuple(
            r.device_name
            for r in s.select(
                sqlalchemy.select(c)
                .select_from(
                    s.t.device_meta_float.join(
                        s.t.device,
                        s.t.device.c.device_name == c,
                    )
                    .join(
                        s.t.beam_path,
                        s.t.beam_path.c.beam_area == s.t.device.c.beam_area,
                    )
                    .join(
                        s.t.device_accessor,
                        s.t.device_accessor.c.device_name == c,
                    )
                )
                .where(
                    s.t.beam_path.c.beam_path == beam_path,
                    s.t.device_meta_float.c.device_meta_name == "sum_l_meters",
                    s.t.device_meta_float.c.device_meta_value
                    < _device_meta(end_device, "sum_l_meters", s),
                    s.t.device.c.device_type == device_type,
                    s.t.device_accessor.c.accessor_name == required_accessor,
                )
                .order_by(s.t.device_meta_float.c.device_meta_value)
            )
        )


def _assert_on_beampath(device, beam_path, select):
    c = select.t.device.c.device_name
    v = select.select_one_or_none(
        sqlalchemy.select(c)
        .select_from(
            select.t.device.join(
                select.t.beam_path,
                select.t.beam_path.c.beam_area == select.t.device.c.beam_area,
            )
        )
        .where(
            select.t.device.c.device_name == device,
            select.t.beam_path.c.beam_path == beam_path,
        ),
        None,
    )
    if v is None:
        raise ValueError(f"device={device} is not in beam_path={beam_path}")


def _device_meta(device, meta, select):
    return select.select_one(
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
    def __init__(self, parser):
        self.counts = PKDict(beam_areas=0, beam_paths=0, devices=0)
        if pykern.pkconfig.in_dev_mode():
            # POSIT: modify parser in place since this is dev mode it'll break only in dev
            # if the parser implementations change from PKDicts.
            _update_dev(parser)
        with _session() as s:
            self._beam_paths(parser.beam_paths, s)
            self._devices(devices.devices, s)

    def _beam_paths(self, parsed, session):
        for a, paths in parsed.items():
            self.counts.beam_areas += 1
            session.insert("beam_area", beam_area=a)
            for p in paths:
                self.counts.beam_paths += 1
                session.insert("beam_path", beam_area=a, beam_path=p)

    def _devices(self, parsed, session):
        def _accessor_meta(accessors):
            for a in accessors:
                a.pksetdefault(_ACCESSOR_META.get(k, _ACCESSOR_META_DEFAULT))
            return accessors

        def _insert(table, values):
            for v in values:
                session.insert(table, **v)

        for d in parsed.values():
            self.counts.devices += 1
            session.insert("device", **d.device)
            _insert("device_meta_float", d.device_meta_float)
            _insert("device_accessor", _accessor_meta(d.device_accessor))

    def _update_dev(parser):
        def _dev_camera_accessors():
            for x in (
                ("acquire", "13SIM1:cam1:Acquire", "bool", 1),
                ("image", "13SIM1:image1:ArrayData", "numpy.ndarray", 0),
                ("n_bits", "13SIM1:cam1:N_OF_BITS", "int", 0),
                ("n_col", "13SIM1:cam1:SizeX", "int", 0),
                ("n_row", "13SIM1:cam1:SizeY", "int", 0),
            ):
                yield PKDict(
                    ("device_name", "accessor_name", "cs_name", "py_type", "writable"),
                    (("DEV_CAMERA",) + x),
                )

        parser.beam_paths.update(DEV_BEAM_PATH=["DEV_AREA"])
        parser.devices.update(
            device=PKDict(
                device_name="DEV_CAMERA",
	        beam_area="DEV_AREA",
                device_type="PROF",
                cs_name="13SIM1",f
            ),
            device_accessor=tuple(_dev_camera_accessors()),
            device_meta_float=[
                PKDict(
                    device_name="DEV_CAMERA",
                    device_meta_name="sum_l_meters",
                    device_meta_value="0.614",
                ),
            ),
        )



class _DevParserWrapper:
    def __init__(self, orig):
        self.beam_paths = orig.beam_paths.pkupdate(self._beam_paths())
        self.devices = orig.devices.pkupdate(

    beam_paths
        return list(values) + [
            PKDict(

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
                cs_name=s,
            ),
            device_accessor=PKDict(
                device_name=p + " foreign",
                accessor_name=p,
                cs_name=s,
                py_type=s,
                writable="bool",
            ),
            device_meta_float=PKDict(
                device_name=p + " foreign",
                device_meta_name=p,
                device_meta_value="float 64",
            ),
        ),
    )


def _path():
    return pykern.pkresource.file_path(
        ".", packages=slicops.config.cfg().package_path
    ).join(_BASE_PATH)


def _session():
    if _meta is None:
        _init()
    return _meta.session()
