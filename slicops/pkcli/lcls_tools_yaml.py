"""Parse `lcls_tools/common/devices/yaml/*.yaml` for `slicops.device_sql_db.recreate`

TODO(robnagler): document, add machine and area_to_machine, beam_path_to_machine

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import copy
import importlib
import pykern.pkio
import pykern.pkyaml
import re
import slicops.device_sql_db
import slicops.const


# We assume the names are valid (could check, but no realy point)
# What this test is doing is ensuring we understand the structure of a pv_base
_PV_POSTFIX_RE = r"([\w.]{1,60}|\w{1,58}:[\w.]{1,58})"

_KNOWN_KEYS = PKDict(
    controls_information=frozenset(("PVs", "control_name", "pv_cache")),
    metadata=frozenset(
        (
            "area",
            "beam_path",
            "bpms_after_wire",
            "bpms_before_wire",
            "l_eff",
            "lblms",
            "hardware",
            "rf_freq",
            "sum_l_meters",
            "type",
        )
    ),
)

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


_TOP_LEVEL_KEYS = frozenset(_KNOWN_KEYS.keys())

_AREAS_MISSING_BEAM_PATH = frozenset(
    (
        "COL",
        "GTL",
        "LI27",
        "LI28",
    ),
)


def create_sql_db():
    """Convert device yaml file to db"""
    return slicops.device_sql_db.recreate(_Parser())


class _Ignore(Exception):
    pass


class _Parser(PKDict):
    def __init__(self):
        self._init()
        self._parse()

    def _init(self):
        self._yaml_glob = (
            pykern.pkio.py_path(
                importlib.import_module("lcls_tools.common.devices.yaml").__file__,
            )
            .dirpath()
            .join("*.yaml")
        )
        self.devices = PKDict()
        self.ctl_keys = set()
        self.meta_keys = set()
        self.beam_paths = PKDict()

    def _parse(self):
        for p in pykern.pkio.sorted_glob(self._yaml_glob):
            if p.basename == "beampaths.yaml":
                continue
            try:
                self._parse_file(pykern.pkyaml.load_file(p), p)
            except Exception:
                pkdlog("ERROR file={}", p)
                raise

    def _parse_file(self, src, path):
        def _input_fixups(name, rec):
            if not rec.controls_information.PVs:
                # Also many don't have beam_path
                raise _Ignore()
            # Save beam_paths for fixups and to return
            if rec.metadata.area not in self.beam_paths:
                self.beam_paths[rec.metadata.area] = tuple(rec.metadata.beam_path)
            if not rec.metadata.beam_path:
                if rec.metadata.area in _AREAS_MISSING_BEAM_PATH:
                    raise _Ignore()
                rec.metadata.beam_path = self.beam_paths[rec.metadata.area]
            if "VCCB" == name:
                # Typo in MEME?
                rec.controls_information.PVs.resolution = "CAMR:LGUN:950:RESOLUTION"
                rec.controls_information.PVs.n_col = "CAMR:LGUN:950:MaxSizeX_RBV"
                rec.controls_information.PVs.n_row = "CAMR:LGUN:950:MaxSizeY_RBV"
                rec.metadata.type = "PROF"
            elif "VCC" == name:
                rec.metadata.type = "PROF"
            if rec.metadata.type == "PROF":
                # No cameras have Acquire for some reason
                rec.controls_information.PVs.pksetdefault(
                    "acquire", f"{rec.controls_information.control_name}:Acquire"
                )
            # TODO(robnagler) parse pv_cache
            return rec

        def _meta(name, raw):
            # TODO validation
            c = raw.controls_information
            m = raw.metadata
            # TODO ignore for now
            raw.metadata.pkdel("hardware")
            self.meta_keys.update(m.keys())
            self.ctl_keys.update(c.keys())
            rv = PKDict(
                name=name,
                cs_name=c.control_name,
            )
            for k in "area", "beam_path":
                if not m.get(k):
                    raise AssertionError(f"missing metadata.{k}")
            rv.metadata = PKDict({k: v for k, v in m.items() if v is not None})
            rv.accessors = PKDict(_pvs(c.PVs, rv))
            return rv

        def _pvs(pvs, rv):
            p = re.compile(rf"^{re.escape(rv.cs_name)}:{_PV_POSTFIX_RE}$")
            for k, v in pvs.items():
                if not (x := p.search(v)):
                    raise ValueError(f"pv={v} does not match regex={p}")
                yield k, v

        def _validate(name, kind, raw):
            if not (t := slicops.const.DEVICE_KINDS_TO_TYPES.get(kind)):
                raise AssertionError(f"unknown kind={kind}")
            if raw.metadata.type not in t:
                raise AssertionError(f"unknown type={raw.metadata.type} expect={t}")
            if x := set(raw.keys()) - _TOP_LEVEL_KEYS:
                raise AssertionError(f"unknown top level keys={s}")
            for x in _TOP_LEVEL_KEYS:
                if y := set(raw[x].keys()) - _KNOWN_KEYS[x]:
                    raise AssertionError(f"unknown {x} keys={y}")
            if not raw.controls_information.PVs:
                raise AssertionError(f"no PVs")
            return name, raw

        for k, x in src.items():
            for n, r in x.items():
                try:
                    self._to_sql_db(
                        n,
                        _meta(
                            *_validate(
                                n,
                                k,
                                _input_fixups(n, copy.deepcopy(r)),
                            )
                        ),
                    )
                except _Ignore:
                    pass
                except Exception:
                    pkdlog("ERROR device={} record={}", n, r)
                    raise

        def _assign(name, rec):
            """Corrections to input data"""

    def _to_sql_db(self, name, rec):
        def _accessor():
            for k, v in rec.accessors.items():
                yield PKDict(device_name=name, accessor_name=k, cs_name=v)

        def _device():
            return PKDict(
                device_name=name,
                beam_area=rec.metadata.area,
                device_type=rec.metadata.type,
                cs_name=rec.cs_name,
            )

        def _meta_float():
            for k, v in rec.metadata.items():
                if k not in _METADATA_SKIP:
                    yield PKDict(
                        device_name=name, device_meta_name=k, device_meta_value=float(v)
                    )

        if name in self.devices:
            raise ValueError(f"duplicate device={name}")
        self.devices[name] = PKDict(
            device=_device(),
            device_accessor=tuple(_accessor()),
            device_meta_float=tuple(_meta_float()),
        )
