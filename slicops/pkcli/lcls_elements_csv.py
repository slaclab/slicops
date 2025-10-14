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


def create_sql_db():
    """Convert device yaml file to db"""
    return slicops.device_sql_db.recreate(_Parser())


class _Parser(PKDict):
    def __init__(self):
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

        with lzma.open("pvs.txt.xz", "rt") as f:
            self._pvs = set(x.strip() for x in f)
        self._keywords = PKDict(_meta(pykern.pkyaml.load_resource("meta")))
        self.devices = PKDict()
        self.beam_paths = PKDict()
        with _csv_path().open("r") as f:
            self._parse_csv(csv.DictReader(f))

    def _parse(self, rows):

        def _one(area, beam_paths, keyword, sum_l_meters):
            # areas that begin with a * are not yet released
            # area that contains a space is not legit and probably NO AREA
            # no beam path means no PVs
            if (
                not beam_paths
                or area.startswith("*")
                or " " in area
                or not (k := self._keywords.get(keyword))
            ):
                return
            if area not in self.beam_paths:
                # assumes that first area with beam_paths is correct
                self.beam_paths[area] = tuple(beam_paths)

        for r in rows:
            _one(
                r["Area"],
                _BEAMPATH_RE.split(r["Beampath"]),
                f["Keyword"],
                round(float(r["sum_l_meters"] or 0), 3),
            )

    # def _input_fixups(name, rec):
    #     if not rec.controls_information.PVs:
    #         # Also many don't have beam_path
    #         raise _Ignore()
    #     # Save beam_paths for fixups and to return
    #     if rec.metadata.area not in self.beam_paths:
    #         self.beam_paths[rec.metadata.area] = tuple(rec.metadata.beam_path)
    #     if not rec.metadata.beam_path:
    #         if rec.metadata.area in _AREAS_MISSING_BEAM_PATH:
    #             raise _Ignore()
    #         rec.metadata.beam_path = self.beam_paths[rec.metadata.area]
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
