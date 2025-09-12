"""Test sliclet

:copyright: Copyright (c) 2025 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""

import pytest


@pytest.mark.asyncio(loop_scope="module")
async def test_all(monkeypatch):
    prev_file_path = None

    def _file_path(path, *args, **kwargs):
        nonlocal prev_file_path
        from pykern import pkinspect, pkdebug

        if path in ("vue", "sliclet/unit.yaml"):
            return pkunit.data_dir().join(path)
        return prev_file_path(path, caller_context=pkinspect.caller_module())

    def _init():
        nonlocal prev_file_path

        import os, sys

        os.environ["SLICOPS_CONFIG_PACKAGE_PATH"] = "somepkg:slicops"

        from pykern import pkunit

        sys.path.insert(0, str(pkunit.data_dir()))

        from pykern import pkresource

        prev_file_path = pkresource.file_path
        monkeypatch.setattr(pkresource, "file_path", _file_path)

    _init()

    from slicops import unit_util
    from pykern import pkunit, pkdebug

    async with unit_util.SlicletSetup("unit", prod=True) as s:
        pkunit.pkeq(b"xyzzy\n", await s.http_get(""))
