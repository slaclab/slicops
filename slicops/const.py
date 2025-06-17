"""Constants

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import itertools

DEVICE_KINDS_TO_TYPES = PKDict(
    bpms=frozenset(("BPM",)),
    lblms=frozenset(("LBLM",)),
    magnets=frozenset(("XCOR", "QUAD", "SOLE", "YCOR", "BEND")),
    screens=frozenset(("PROF",)),
    tcavs=frozenset(("LCAV",)),
    wires=frozenset(("WIRE",)),
)

DEVICE_TYPES = frozenset(itertools.chain.from_iterable(DEVICE_KINDS_TO_TYPES.values()))
