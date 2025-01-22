"""Convert `lcls_tools.common.devices.yaml`

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import pykern.pkio
import pykern.pkyaml
import inspect
import lcls_tools.common.devices.yaml
import re

_MODULE_BASE = "device_meta_raw"

# We assume the names are valid (could check, but no realy point)
# What this test is doing is ensuring we understand the structure of a pv_base
_PV_BASE_RE = r"(\w{1,60}|\w{1,58}:\w{1,58})"


def to_python():
    return _Parser().to_python()


class _Parser:
    def __init__(self):
        self._maps = PKDict(
            BEAMSPATHS_TO_DEVICES=PKDict(),
            AREAS_TO_DEVICES=PKDict(),
            DEVICES_TO_AREAS=PKDict(),
            AREAS_TO_BEAMPATHS=PKDict(),
            DEVICE_TO_META=PKDict(),
            DEVICE_KIND_TO_DEVICES=PKDict(),
        )
        for p in self._paths():
            try:
                self._parse_file(pykern.pkyaml.load_file(p))
            except Exception:
                pkdlog("ERROR file={}", p)
                raise

    def _parse_file(self, src):

        def _fixups(device, rec):
            """Corrections to input data"""
            if device == "VCCB":
                rec.controls_information.PVs.resolution = "CAMR:LGUN:950:RESOLUTION"

        def _assign(device, meta):
            """Corrections to input data"""
            if d := self._maps.DEVICE_TO_META.get(n):
                raise ValueError(f"duplicate device={n} record={r} first meta={d}")
            self._maps.DEVICE_TO_META[n] = meta

        def _meta(device, ctl, md, kind):
            rv = PKDict(pv_prefix=ctl.control_name, device_kind=kind, pv_base=PKDict())
            p = re.compile(rf"^{re.escape(rv.pv_prefix)}:{_PV_BASE_RE}$")
            for v in ctl.PVs.values():
                if not (m := p.search(v)):
                    raise ValueError(
                        f"invalid pv name={v} for device={device} regex={p}"
                    )
                # TODO(robnagler) refine type based on name
                rv.pv_base[m.group(1)] = PKDict(pv_name=v, pv_type="int")
            return rv.pkupdate(
                # TODO(robnagler) meta.type is not always set (see vcc.yaml)
                area=md.area,
                beam_path=md.beam_path,
                device_length=md.sum_l_meters,
            )

        if not (s := src.get("screens")):
            return
        for n, r in s.items():
            try:
                _fixups(n, r)
                _assign(n, _meta(n, r.controls_information, r.metadata, "screen"))
            except Exception:
                pkdlog("ERROR device={} record={}", n, r)
                raise

    def _paths(self):
        return pykern.pkio.sorted_glob(
            pykern.pkio.py_path(lcls_tools.common.devices.yaml.__file__)
            .dirpath()
            .join("*.yaml")
        )

    def _python_dir(self):
        return (
            pykern.pkio.py_path(inspect.getmodule(self).__file__)
            .dirpath()
            .new(basename=_MODULE_BASE)
        )

    def to_python(self):
        pass
