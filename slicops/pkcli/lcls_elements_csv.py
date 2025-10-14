"""Parse `lcls_tools/common/devices/yaml/lcls_elements.csv` for `slicops.device_sql_db.recreate`

TODO(robnagler): only includes what is used in slicops and slactwin at the moment

TODO(robnagler): uses a cached meme-pvs.txt.xz which is created by ``meme.names.list_pvs("%", sort_by="z")``

TODO(robnagler): add machine and area_to_machine, beam_path_to_machine

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import pykern.pkyaml
import pykern.pkresource
import lzma
import csv
import re

_BEAMPATH_RE = re.compile(" *, *")

_PV_RE = re.compile("^(.+):(.+)$")

def create_sql_db(meme_pvs):
    """Convert device yaml file to db"""
    return slicops.device_sql_db.recreate(_Parser(meme_pvs))


class _Parser(PKDict):
    def __init__(self, meme_pvs):
        def _csv_path():
            return (
                pykern.pkio.py_path(
                    importlib.import_module("lcls_tools.common.devices.yaml").__file__,
                )
                .dirpath()
                .join("lcls_element.csv")
            )

        def _meta(raw):
            for t, v in raw.items():
                for k in v.pkdel(keywords):
                    yield k, PKDict(device_type=t).pkupdate(v)

        def _pv_split(lines):
            for l in lines:
                if not (m := _PV_RE.search(l)):
                    continue
                self._pvs.setdefault(m.group(0), set()).add(m.group(1))

        self._pvs = PKDict()
        with lzma.open(meme_pvs, "rt") as f:
            _pvs(x.strip() for x in f)
        self._keywords = PKDict(_meta(pykern.pkyaml.load_resource("meta")))
        self.devices = PKDict()
        self.beam_paths = PKDict()
        with _csv_path().open("r") as f:
            self._parse_csv(csv.DictReader(f))

    def _parse(self, rows):

        def _accessors(accessors, pvs, cs_name, device_name):
            if pvs:
                return []
            rv = []
            for s, a in accessors.items():
                if s.split(".")[0] not in pvs:
                    continue
                rv.append(
                    PKDict(
                        device_name=device_name,
                        cs_name=cs_name + ": " + s,
                    ),
                )
            return rv

        def _one(device_name, area, beam_paths, keyword, cs_name, sum_l_meters):
            # areas that begin with a * are not yet released
            # area that contains a space is not legit and probably NO AREA
            # no beam path means no PVs
            if (
                not beam_paths
                or area.startswith("*")
                or " " in area
                or not (m := self._keywords.get(keyword))
            ):
                return
            if area not in self.beam_paths:
                # assumes that first area with beam_paths is correct
                self.beam_paths[area] = tuple(beam_paths)
            if not (a := _accessors(meta.accessors, self._pvs.get(cs_name), cs_name, device_name)):
                return
            return PKDict(
                device=PKDict(
                    device_name=device_name,
                    device_type=meta.device_type,
                    beam_area=area,
                    cs_name=cs_name,
                ),
                device_accessors=a,
                device_meta_float=[
                    PKDict(
                        device_name=device_name,
                        device_meta_name="sum_l_meters",
                        device_meta_value=sum_l_meters,
                    )
                ],
            )


        for r in rows:
            _one(
                r["Element"],
                r["Area"],
                _BEAMPATH_RE.split(r["Beampath"]),
                r["Keyword"],
                r["Control System Name"],
                r["sum_l_meters"] and round(float(r["sum_l_meters"]), 3),
            )

    # def _input_fixups(name, rec):
    #     if "VCCB" == name:
    #         # Typo in MEME?
    #         rec.controls_information.PVs.resolution = "CAMR:LGUN:950:RESOLUTION"
    #         rec.controls_information.PVs.n_col = "CAMR:LGUN:950:MaxSizeX_RBV"
    #         rec.controls_information.PVs.n_row = "CAMR:LGUN:950:MaxSizeY_RBV"
    #         rec.metadata.type = "PROF"
    #     elif "VCC" == name:
    #         rec.metadata.type = "PROF"
    #     if rec.metadata.type == "PROF":
    #         # No cameras have Acquire for some reason
    #         rec.controls_information.PVs.pksetdefault(
    #             "acquire", f"{rec.controls_information.control_name}:Acquire"
    #         )
    #     # TODO(robnagler) parse pv_cache
    #     return rec
