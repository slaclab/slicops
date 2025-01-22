"""Convert `lcls_tools.common.devices.yaml` to `slicops.device_meta_raw`

TODO(robnagler): document, correct types, add machine and area_to_machine, beam_path_to_machine

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import importlib
import inspect
import pprint
import pykern.pkcli.fmt
import pykern.pkio
import pykern.pkyaml
import re

_MODULE_BASE = "device_meta_raw.py"

# We assume the names are valid (could check, but no realy point)
# What this test is doing is ensuring we understand the structure of a pv_base
_PV_BASE_RE = r"(\w{1,60}|\w{1,58}:\w{1,58})"

# Eventually would be canonical
_DEVICE_KIND_TO_ACCESSOR = PKDict(
    screen=PKDict(
        {
            "Acquire": PKDict(name="acquire", py_type="bool", pv_writable=True),
            "IMAGE": PKDict(name="image", py_type="ndarray"),
            "Image:ArrayData": PKDict(name="image", py_type="ndarray"),
            "Image:ArraySize0_RBV": PKDict(name="num_rows"),
            "Image:ArraySize1_RBV": PKDict(name="num_cols"),
            "Image:ArraySizeX_RBV": PKDict(name="num_rows"),
            "Image:ArraySizeY_RBV": PKDict(name="num_cols"),
            "N_OF_BITS": PKDict(name="bit_depth"),
            "N_OF_COL": PKDict(name="num_cols"),
            "N_OF_ROW": PKDict(name="num_rols"),
            # Devlement: AreaDetector SimDetector default definitions
            # TODO(robnagler) simplify the st.cmd for the SimDetector
            "cam1:ArraySizeX_RBV": PKDict(name="num_rows"),
            "cam1:ArraySizeY_RBV": PKDict(name="num_cols"),
            "cam1:N_OF_BITS": PKDict(name="bit_depth"),
            "image1:ArrayData": PKDict(name="image", py_type="ndarray"),
        }
    )
)

# TODO(robnagler) should be dynamic, but need to add to paths so easiest to add here for now
_DEV_YAML = """
screens:
  DEV_CAMERA:
    controls_information:
      PVs:
        image: 13SIM1:image1:ArrayData
        n_col: 13SIM1:cam1:ArraySizeX_RBV
        n_row: 13SIM1:cam1:ArraySizeY_RBV
        n_bits: 13SIM1:cam1:N_OF_BITS
      control_name: 13SIM1
    metadata:
      area: DEV_AREA
      beam_path:
      - DEV_BEAM_PATH
      sum_l_meters: 0.614
      type: PROF
"""


def to_python():
    return _Parser().output_path


class _Parser:
    def __init__(self):
        self._map = PKDict(
            AREA_TO_BEAM_PATH=PKDict(),
            AREA_TO_DEVICE=PKDict(),
            BEAM_PATH_TO_AREA=PKDict(),
            BEAM_PATH_TO_DEVICE=PKDict(),
            DEVICE_KIND_TO_DEVICE=PKDict(),
            DEVICE_TO_AREA=PKDict(),
            DEVICE_TO_META=PKDict(),
        )
        self._init_paths()
        self._parse()
        self._denormalize()
        self.output_path.write(self._to_python())
        pykern.pkcli.fmt.run(str(self.output_path))

    def _denormalize(self):
        def _append(map_, name, value):
            if isinstance(name, tuple):
                for n in name:
                    _append_one(map_, n, value)
            else:
                _append_one(map_, name, value)

        def _append_one(map_, name, value):
            m = self._map[map_].pksetdefault(name, set)[name]
            if isinstance(value, tuple):
                m.update(value)
            else:
                m.add(value)

        def _sort(map_):
            for k, v in map_.items():
                if isinstance(v, PKDict):
                    _sort(v)
                elif isinstance(v, set):
                    map_[k] = tuple(sorted(v))

        for d, m in self._map.DEVICE_TO_META.items():
            try:
                _append("AREA_TO_BEAM_PATH", m.area, m.beam_path)
                _append("AREA_TO_DEVICE", m.area, d)
                _append("BEAM_PATH_TO_AREA", m.beam_path, m.area)
                _append("BEAM_PATH_TO_DEVICE", m.beam_path, d)
                _append("DEVICE_KIND_TO_DEVICE", m.device_kind, d)
                _append("DEVICE_TO_AREA", d, m.area)
            except Exception:
                pkdlog("ERROR device={} meta={}", d, m)
                raise
        _sort(self._map)

    def _init_paths(self):
        m = inspect.getmodule(self)
        self._this_module_name = m.__name__
        self._this_module_path = pykern.pkio.py_path(m.__file__)
        self._yaml_glob = (
            pykern.pkio.py_path(
                importlib.import_module("lcls_tools.common.devices.yaml").__file__
            )
            .dirpath()
            .join("*.yaml")
        )
        self.output_path = self._this_module_path.dirpath().new(basename=_MODULE_BASE)

    def _parse(self):
        for p in pykern.pkio.sorted_glob(self._yaml_glob):
            try:
                self._parse_file(pykern.pkyaml.load_file(p))
            except Exception:
                pkdlog("ERROR file={}", p)
                raise
        if pykern.pkconfig.in_dev_mode():
            self._parse_file(pykern.pkyaml.load_str(_DEV_YAML))

    def _parse_file(self, src):

        def _accessor(meta):
            a = _DEVICE_KIND_TO_ACCESSOR[meta.device_kind]
            return PKDict(
                {
                    a[k]
                    .name: a[k]
                    .copy()
                    .pksetdefault(pv_base=k, pv_name=v, py_type="int")
                    for k, v in meta.pv_base.items()
                }
            )

        def _assign(device, meta):
            """Corrections to input data"""
            if d := self._map.DEVICE_TO_META.get(n):
                raise ValueError(f"duplicate device={n} record={r} first meta={d}")
            self._map.DEVICE_TO_META[n] = meta

        def _input_fixups(device, rec):
            """Corrections to input data"""
            # TODO(robnagler) when there is resolution
            # if device == "VCCB":
            #    rec.controls_information.PVs.resolution = "CAMR:LGUN:950:RESOLUTION"
            # Don't need resolution
            rec.controls_information.PVs.pkdel("resolution")
            if rec.metadata.sum_l_meters is None:
                # eg. LI25.yaml OTR22
                return False
            if not rec.controls_information.PVs:
                # eg. UNDH.yaml BODCBX40
                return False
            return True

        def _meta(device, ctl, md, kind):
            rv = PKDict(pv_prefix=ctl.control_name, device_kind=kind, pv_base=PKDict())
            p = re.compile(rf"^{re.escape(rv.pv_prefix)}:{_PV_BASE_RE}$")
            for v in ctl.PVs.values():
                if not (m := p.search(v)):
                    raise ValueError(
                        f"invalid pv name={v} for device={device} regex={p}"
                    )
                rv.pv_base[m.group(1)] = v
            return rv.pkupdate(
                # TODO(robnagler) meta.type is not always set (see vcc.yaml), so ignoring for now
                area=md.area,
                beam_path=tuple(sorted(md.beam_path)),
                device_length=md.sum_l_meters,
                device_name=device,
            )

        def _meta_fixups(meta):
            meta.pv_base.Acquire = f"{meta.pv_prefix}:Acquire"
            meta.accessor = _accessor(meta)
            return meta

        if not (s := src.get("screens")):
            return
        for n, r in s.items():
            try:
                if not _input_fixups(n, r):
                    continue
                _assign(
                    n,
                    _meta_fixups(
                        _meta(n, r.controls_information, r.metadata, "screen")
                    ),
                )
            except Exception:
                pkdlog("ERROR device={} record={}", n, r)
                raise

    def _to_python(
        self,
    ):
        def _header():
            return f'''"""Raw device data

**DO NOT EDIT; automatically generated**

* generator: {self._this_module_name}
* input: {self._yaml_glob}

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict


DB = '''

        def _pkdict(py):
            return py.replace("{", "PKDict({").replace("}", "})")

        return _header() + _pkdict(pprint.pformat(self._map, indent=4, width=120))
