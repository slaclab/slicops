"""Convert `lcls_tools.common.devices.yaml` to `slicops.device_meta_raw`

TODO(robnagler): document, correct types, add machine and area_to_machine, beam_path_to_machine

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import importlib

# import pykern.device_db
import pykern.pkio
import pykern.pkyaml
import re

from pykern import pkjson


# We assume the names are valid (could check, but no realy point)
# What this test is doing is ensuring we understand the structure of a pv_base
_PV_POSTFIX_RE = r"([\w.]{1,60}|\w{1,58}:[\w.]{1,58})"

# Eventually would be canonical
_DEVICE_KIND_TO_ACCESSOR = PKDict(
    screen=PKDict(
        {
            # Everything here should have py_type
            "Acquire": PKDict(name="acquire", py_type="bool", pv_writable=True),
            "Gain": PKDict(name="gain", pv_writable=True, py_type="int"),
            "IMAGE": PKDict(name="image", py_type="ndarray"),
            "Image:ArrayData": PKDict(name="image", py_type="ndarray"),
            "Image:ArraySize0_RBV": PKDict(name="num_rows", py_type="int"),
            "Image:ArraySize1_RBV": PKDict(name="num_cols", py_type="int"),
            "Image:ArraySizeX_RBV": PKDict(name="num_cols", py_type="int"),
            "Image:ArraySizeY_RBV": PKDict(name="num_rows", py_type="int"),
            "N_OF_BITS": PKDict(name="bit_depth", py_type="int"),
            "N_OF_COL": PKDict(name="num_cols", py_type="int"),
            "N_OF_ROW": PKDict(name="num_rows", py_type="int"),
            # Devlement: AreaDetector SimDetector default definitions
            # TODO(robnagler) simplify the st.cmd for the SimDetector
            "cam1:SizeX": PKDict(name="num_cols", py_type="int"),
            "cam1:SizeY": PKDict(name="num_rows", py_type="int"),
            "cam1:N_OF_BITS": PKDict(name="bit_depth", py_type="int"),
            "cam1:Acquire": PKDict(name="acquire", py_type="bool", pv_writable=True),
            "cam1:Gain": PKDict(name="gain", pv_writable=True, py_type="int"),
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
"""


def create_from_yaml():
    """Convert device yaml file to db"""
    pass  # return slicops.device_db_sql.recreate(tuple(_Parser().devices.values()))


def parse():
    r = pykern.pkio.mkdir_parent("raw")
    x = set()
    for d in _Parser().devices.values():
        x.update(d.attrs.keys())
        pykern.pkjson.dump_pretty(
            d,
            filename=pykern.pkio.mkdir_parent(r.join(d.device_kind, d.area)).join(
                d.device_name + ".json"
            ),
        )
    return x


class _Parser:
    def __init__(self):
        self._init()
        self._parse()

    def _init(self):
        self._yaml_glob = (
            pykern.pkio.py_path(
                pkdp(importlib.import_module("lcls_tools.common.devices.yaml").__file__)
            )
            .dirpath()
            .join("*.yaml")
        )
        self.devices = PKDict()

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

        def _accessor(meta):
            a = _DEVICE_KIND_TO_ACCESSOR.screen  # [meta.device_kind]
            for k, v in meta.pv_base.items():
                rv = a[k].copy() if k in a else PKDict()
                yield k, rv.pksetdefault(pv_base=k, pv_name=v)

        def _assign(device, meta):
            """Corrections to input data"""
            if d := self.devices.get(n):
                raise ValueError(f"duplicate device={n} record={r} first meta={d}")
            self.devices[n] = meta

        def _input_fixups(device, rec):
            """NOT USED Corrections to input data"""
            # TODO(robnagler) when there is resolution
            if device == "VCCB":
                rec.controls_information.PVs.resolution = "CAMR:LGUN:950:RESOLUTION"
            return
            # Don't need resolution
            # rec.controls_information.PVs.pkdel("resolution")
            if rec.metadata.sum_l_meters is None:
                # eg. LI25.yaml OTR22
                return False
            if not rec.controls_information.PVs:
                # eg. UNDH.yaml BODCBX40
                return False
            return True

        def _meta(device, ctl, md, kind, raw):
            rv = PKDict(pv_prefix=ctl.control_name, device_kind=kind, pv_base=PKDict())
            p = re.compile(rf"^{re.escape(rv.pv_prefix)}:{_PV_POSTFIX_RE}$")
            # TODO(robnagler) type and kind are different, or kind
            for v in ctl.PVs.values():
                if not (m := p.search(v)):
                    raise ValueError(
                        f"invalid pv name={v} for device={device} regex={p}"
                    )
                rv.pv_base[m.group(1)] = v
            rv.pkupdate(
                area=md.area,
                beam_path=tuple(sorted(md.beam_path)),
                device_name=device,
                # Not always a type(?)
                device_type=md.get("type"),
            )
            md.pkdel("beam_path")
            md.pkdel("area")
            md.pkdel("type")
            # TODO robnagler list of attrs {'bpms_before_wire', 'bpms_after_wire', 'l_eff', 'lblms', 'rf_freq', 'sum_l_meters'}
            rv.attrs = md
            return rv

        def _meta_fixups(meta):
            # TODO(robnagler): DEV_CAMERA is special, need to configure it right
            # if meta.device_name != "DEV_CAMERA":
            #    meta.pv_base.pksetdefault(
            #        Acquire=f"{meta.pv_prefix}:Acquire",
            #    )
            meta.accessor = PKDict(_accessor(meta))
            # No longer needed
            meta.pkdel("pv_base")
            return meta

        for k, x in src.items():
            for n, r in x.items():
                try:
                    _input_fixups(n, r)
                    # if not _input_fixups(n, r):
                    #    continue
                    _assign(
                        n,
                        _meta_fixups(
                            # remove the s as all the kinds are plural
                            # TODO(robnagler) look up these in table
                            #   reconcile with type
                            _meta(n, r.controls_information, r.metadata, k[:-1], r)
                        ),
                    )
                except Exception:
                    pkdlog("ERROR device={} record={}", n, r)
                    raise
