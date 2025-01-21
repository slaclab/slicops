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

_MODULE_BASE = "device_meta_raw";

def to_module():
    return _Parser().to_python()

def _Parser:
    def __init__(self):
        self._maps = PKDict(
            BEAMSPATHS_TO_DEVICES=PKDict(),
            AREAS_TO_DEVICES=PKDict(),
            DEVICES_TO_AREAS=PKDict(),
            AREAS_TO_BEAMPATHS=PKDict(),
            DEVICE_TO_PV_META=PKDict(),
            DEVICE_KIND_TO_DEVICES=PKDict(),
        )
        for p in self._paths():
            self._parse_one(pykern.pkyaml.load_file(p))

    def to_python(self):
        pass

    def _paths(self):
        return pykern.pkio.sorted_glob(pykern.pkio.py_path(lcls_tools.common.devices.yaml.__file__).join("*.yml"))

    def _python_dir(self):
        return pykern.pkio.py_path(inspect.getmodule(self).__file__).dirpath().new(basename=_MODULE_BASE)
