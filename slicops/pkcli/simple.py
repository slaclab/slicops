"""Read/write a file with state

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import pykern.util
import pykern.pkyaml
import pykern.pkcli


def read():
    """Convert the db into PKDict

    Returns:
        PKDict: values in the db
    """
    return pykern.pkyaml.load_file(_path())


def write(*key_value_pairs):
    """Update db with key=value arguments or single dict as arg

    Args:
        key_value_pairs (str): list of key_value_pairs or single dict
    """
    def _values():
        if not key_value_pairs:
            pykern.command_error("pass at least one key=value pair")
        if isinstance(key_value_pairs[0], str):
            return (a.split("=", 1) for a in key_value_pairs)
        # can be a generator or a dict or anything that can turn into a dict
        return key_value_pairs[0]

    pykern.pkyaml.dump_pretty(PKDict(_values()), _path())
    return read()


def _path():
    return pykern.util.dev_run_dir(_path).join("simple.yaml")
