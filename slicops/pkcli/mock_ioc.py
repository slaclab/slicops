"""IOC configured from a YAML file

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import asyncio
import caproto.server
import pykern.fconf
import pykern.pkio


def run(config_dir):
    def _normalize(raw):
        for k, v in raw.items():
            if not isinstance(v, dict):
                v = PKDict(value=v)
            v.pksetdefault(delay=1, value=None)
            for t in v.get("triggers", []):
                t.pksetdefault(delay=1)
            yield k, v

    def _pvgroup(config):
        return PKDict(
            # Need to hardwire the defaults, because ioc_arg_parser uses
            # argparse globally which causes a mess with argh (which uses argparse)
            pvdb=_PVGroup(config, macros={}, prefix="").pvdb,
            interfaces=["0.0.0.0"],
            module_name="caproto.asyncio.server",
            log_pv_names=False,
        )

    caproto.server.run(
        **_pvgroup(
            PKDict(_normalize(pykern.fconf.parse_all(pykern.pkio.py_path(config_dir)))),
        ),
    )


class _PVGroup(caproto.server.PVGroup):

    def __init__(self, config, *args, **kwargs):
        self.__config = config
        for k, v in self.__config.items():
            self._pvs_[k] = p = caproto.server.pvproperty(
                startup=self.__startup,
                value=v.value,
            )
            p.__set_name__(self, k)
        super().__init__(*args, **kwargs)

    async def xgroup_write(self, instance, value):
        pkdp((instance, value))
        return

    async def __startup(self, _ignore_self, pv, async_lib):
        # async_lib doesn't have create taxsk
        # _ignore_self needed to match signature checking in caproto
        # pkdp("{} {}", pv.name, async_lib)
        # asyncio.create_task(self.__publish(pv))
        pass

    async def __publish(self, pv):
        pass
