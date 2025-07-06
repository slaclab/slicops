"""Read/write a file with state

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import pykern.pkcli
import pykern.pkio
import pykern.pkresource
import pykern.pkyaml
import pykern.util
import slicops.ctx

_SCHEMA = None


def path():
    return pykern.util.dev_run_dir(path).join("simple_db.yaml")


def read():
    """Convert the db into PKDict.

    If not found, returns empty PKDict() with a warning.

    Returns:
        PKDict: values in the db
    """
    rv = _read(path())
    if rv is None:
        return PKDict()
    return rv


def write(*key_value_pairs):
    """Update db with key=value arguments or single dict as arg

    Args:
        key_value_pairs (str): list of key_value_pairs or single dict
    """

    def _pairs():
        if not key_value_pairs:
            pykern.command_error("pass at least one key=value pair")
        if isinstance(key_value_pairs[0], str):
            return (a.split("=", 1) for a in key_value_pairs)
        if isinstance(key_value_pairs[0], dict):
            return key_value_pairs[0].items()
        return key_value_pairs[0]

    def _read_or_new(old, new):
        # Atomic read/write
        if old.exists():
            old.copy(new)
            return _read(new)
        return PKDict()

    o = path()
    n = o.new(ext="tmp" + pykern.util.random_base62())
    try:
        rv = _read_or_new(o, n).pkupdate(_validate(_pairs()))
        pykern.pkyaml.dump_pretty(rv, n)
        n.rename(o)
    finally:
        pykern.pkio.unchecked_remove(n)
    return rv


def _read(path):
    try:
        # TODO(robnagler) should validate
        return pykern.pkyaml.load_file(path)
    except Exception as e:
        if pykern.pkio.exception_is_not_found(e):
            pkdlog("ignoring not found path={}", path)
            return None
        raise


def _validate(pairs):
    ctx = slicops.ctx.Ctx("simple")
    for k, v in pairs:
        yield k, ctx.fields[k].value_set(v)
