"""Convert `lcls_tools.common.devices.yaml` to `slicops.device_meta_raw`

TODO(robnagler): document, correct types, add machine and area_to_machine, beam_path_to_machine

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

# Eventually would be canonical
# TODO(robnagler) should be dynamic, but need to add to paths so easiest to add here for now
_DEV_YAML = """
screens:
  DEV_CAMERA:
    controls_information:
      PVs:
        acquire: 13SIM1:cam1:Acquire
        gain: 13SIM1:cam1:Gain
        image: 13SIM1:image1:ArrayData
        n_col: 13SIM1:cam1:SizeX
        n_row: 13SIM1:cam1:SizeY
        n_bits: 13SIM1:cam1:N_OF_BITS
      control_name: 13SIM1
    metadata:
      area: DEV_AREA
      beam_path:
      - DEV_BEAM_PATH
      sum_l_meters: 0.614
      type: PROF
"""


_KNOWN_KEYS = PKDict(
    controls_information=frozenset(("PVs", "control_name")),
    metadata=frozenset(
        (
            "area",
            "beam_path",
            "bpms_after_wire",
            "bpms_before_wire",
            "l_eff",
            "lblms",
            "rf_freq",
            "sum_l_meters",
            "type",
        )
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


def yaml_to_sql():
    """Convert device yaml file to db"""
    return slicops.device_sql_db.recreate(_Parser())


def parse():
    from pykern import pkjson

    p = _Parser()
    return len(p.devices)
    r = pykern.pkio.mkdir_parent("raw")
    for d in p.devices.values():
        pkjson.dump_pretty(
            d,
            filename=pykern.pkio.mkdir_parent(
                r.join(d.metadata.type, d.metadata.area)
            ).join(d.name + ".json"),
        )


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
        self.accessors = PKDict()
        self.pvs = set()
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
        if pykern.pkconfig.in_dev_mode():
            self._parse_file(
                pykern.pkyaml.load_str(_DEV_YAML), pykern.pkio.py_path(".")
            )

    def _parse_file(self, src, path):
        def _assign(name, rec):
            """Corrections to input data"""
            if name in self.devices:
                raise ValueError(f"duplicate device={name}")
            self.devices[name] = rec

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
            return rec

        def _meta(name, raw):
            # TODO validation
            c = raw.controls_information
            m = raw.metadata
            self.meta_keys.update(m.keys())
            self.ctl_keys.update(c.keys())
            rv = PKDict(
                name=name,
                pv_prefix=c.control_name,
            )
            for k in "area", "beam_path":
                if not m.get(k):
                    raise AssertionError(f"missing metadata.{k}")
            rv.metadata = PKDict({k: v for k, v in m.items() if v is not None})
            rv.pvs = PKDict(_pvs(c.PVs, rv))
            return rv

        def _pvs(pvs, rv):
            p = re.compile(rf"^{re.escape(rv.pv_prefix)}:{_PV_POSTFIX_RE}$")
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
            for x in ("controls_information", "metadata"):
                if y := set(raw[x].keys()) - _KNOWN_KEYS[x]:
                    raise AssertionError(f"unknown {x} keys={y}")
            if not raw.controls_information.PVs:
                raise AssertionError(f"no PVs")
            return name, raw

        for k, x in src.items():
            for n, r in x.items():
                try:

                    _assign(
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
