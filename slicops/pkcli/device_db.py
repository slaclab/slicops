"""Convert `lcls_tools.common.devices.yaml` to `slicops.device_meta_raw`

TODO(robnagler): document, correct types, add machine and area_to_machine, beam_path_to_machine

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import importlib
import pykern.device_db
import pykern.pkio
import pykern.pkyaml
import re

# We assume the names are valid (could check, but no realy point)
# What this test is doing is ensuring we understand the structure of a pv_base
_PV_BASE_RE = r"(\w{1,60}|\w{1,58}:\w{1,58})"

# Eventually would be canonical
_DEVICE_KIND_TO_ACCESSOR = PKDict(
    screen=PKDict(
        {
            "Acquire": PKDict(name="acquire", py_type="bool", pv_writable=True),
            "Gain": PKDict(name="gain", pv_writable=True),
            "IMAGE": PKDict(name="image", py_type="ndarray"),
            "Image:ArrayData": PKDict(name="image", py_type="ndarray"),
            "Image:ArraySize0_RBV": PKDict(name="num_rows"),
            "Image:ArraySize1_RBV": PKDict(name="num_cols"),
            "Image:ArraySizeX_RBV": PKDict(name="num_cols"),
            "Image:ArraySizeY_RBV": PKDict(name="num_rows"),
            "N_OF_BITS": PKDict(name="bit_depth"),
            "N_OF_COL": PKDict(name="num_cols"),
            "N_OF_ROW": PKDict(name="num_rows"),
            # Devlement: AreaDetector SimDetector default definitions
            # TODO(robnagler) simplify the st.cmd for the SimDetector
            "cam1:SizeX": PKDict(name="num_cols"),
            "cam1:SizeY": PKDict(name="num_rows"),
            "cam1:N_OF_BITS": PKDict(name="bit_depth"),
            "cam1:Acquire": PKDict(name="acquire", py_type="bool", pv_writable=True),
            "cam1:Gain": PKDict(name="gain", pv_writable=True),
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
      array_is_row_major: true
"""


def to_python():
    """Convert device yaml file to python file

    Returns:
      pykern.pkio.py_path: Path of python file
    """
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

    def _init_paths(self):
        self._yaml_glob = (
            pykern.pkio.py_path(
                importlib.import_module("lcls_tools.common.devices.yaml").__file__
            )
            .dirpath()
            .join("*.yaml")
        )

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
            rv = PKDict(
                {
                    a[k]
                    .name: a[k]
                    .copy()
                    .pksetdefault(pv_base=k, pv_name=v, py_type="int")
                    for k, v in meta.pv_base.items()
                    if k in a
                }
            )
            if "image" in rv:
                rv.image.array_is_row_major = meta.array_is_row_major
            return rv

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
                array_is_row_major=md.get("array_is_row_major", True),
                # TODO(robnagler) meta.type is not always set (see vcc.yaml), so ignoring for now
                area=md.area,
                beam_path=tuple(sorted(md.beam_path)),
                device_length=md.sum_l_meters,
                device_name=device,
            )

        def _meta_fixups(meta):
            # TODO(robnagler): DEV_CAMERA is special, need to configure it right
            if meta.device_name != "DEV_CAMERA":
                meta.pv_base.pksetdefault(
                    Acquire=f"{meta.pv_prefix}:Acquire",
                )
            meta.accessor = _accessor(meta)
            # No longer needed
            meta.pkdel("pv_base")
            meta.pkdel("array_is_row_major")
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

    def _to_db(self):
        self._map
