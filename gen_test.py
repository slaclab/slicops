"""Test generators

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

# This is here only to allow pretty printing the examples more easily.
# In tests we defer imports (put inside test functions) so import errors have correct context.
from pykern import pkunit, pkio, pkdebug
from pykern.pkcollections import PKDict
import collections
import re


def test_readlines():
    with pkio.save_chdir(pkunit.data_dir()):
        pkdebug.pkdp(count_calls())
        pkunit.pkeq(count_calls(), count_calls_gen())


_PAT = re.compile(r"215:log call .* (\w+)>")


def count_calls():
    with open("api.log") as f:
        rv = PKDict()
        for x in f:
            if m := _PAT.search(x):
                rv[m.group(1)] = rv.get(m.group(1), 0) + 1
    return rv


def count_calls_gen():
    def _calls():
        with open("api.log") as f:
            for x in f:
                if m := _PAT.search(x):
                    yield m.group(1)

    return PKDict(collections.Counter(_calls()))
