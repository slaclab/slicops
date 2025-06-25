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

_SCHEMA = None


def path():
    return pykern.util.dev_run_dir(path).join("simple.yaml")


def read():
    """Convert the db into PKDict

    Returns:
        PKDict: values in the db
    """
    return pykern.pkyaml.load_file(path())


def schema():
    global _SCHEMA

    if not _SCHEMA:
        _SCHEMA = pykern.pkyaml.load_file(
            pykern.pkresource.file_path("schema/simple.yaml")
        )
    return _SCHEMA


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
        if isinstance(key_value_pairs[0], dict):
            return key_value_pairs[0].items()
        return key_value_pairs[0]

    # TODO(robnagler) pkyaml needs to return dumped value
    t = path().new(ext="tmp" + pykern.util.random_base62())
    pykern.pkyaml.dump_pretty(read().pkupdate(_validate(_values())), t)
    t.rename(path())
    return read()


def _validate(values):
    def _button(name, decl, value):
        raise ValueError(f"button={name} may not be written")

    def _float(name, decl, value):
        return _number(name, decl, float(value))

    def _integer(name, decl, value):
        return _number(name, decl, int(value))

    def _number(name, decl, value):
        if (m := decl.get("min")) is not None:
            if value < m:
                raise ValueError(
                    f"value={value} is less than min={m} for {decl.widget}={name}"
                )
        if (m := decl.get("max")) is not None:
            if value > m:
                raise ValueError(
                    f"value={value} is greater than max={m} for {decl.widget}={name}"
                )
        return value

    def _select(name, decl, value):
        for c in decl.choices:
            if c.code == value:
                return value
        raise ValueError(f"value={value} invalid for select={name}")

    def _static(name, decl, value):
        if value is None:
            return ""
        return value

    s = schema()
    for k, v in values:
        if not (f := s.get(k)):
            raise KeyError(f"name={k} not valid field")
        if "integer" == f.widget:
            v = _integer(k, f, v)
        elif "float" == f.widget:
            v = _float(k, f, v)
        elif "select" == f.widget:
            v = _select(k, f, v)
        elif "static" == f.widget:
            v = _static(k, f, v)
        elif "button" == f.widget:
            v = _button(k, f, v)
        else:
            raise AssertionError(f"widget={f.widget} not supported")
        yield k, v
