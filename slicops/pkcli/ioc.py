"""IOC configured from a YAML file

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp, pkdexc
import asyncio
import caproto.server
import numpy
import pykern.fconf
import pykern.pkio
import pykern.pkyaml


def run(init_yaml, db_yaml=None):
    def _fconf():
        p = pykern.pkio.py_path(init_yaml)
        if p.check(dir=True):
            return pykern.fconf.parse_all(p)
        if p.check() and p.ext:
            return pykern.fconf.Parser([p]).result
        return pykern.fconf.parse_all(path=p.dirpath(), glob=p.basename + "*")

    def _normalize(raw):
        for k, v in raw.items():
            if not isinstance(v, dict):
                v = PKDict(value=v)
            v.pksetdefault(delay=1, value=None, dispatch=PKDict)
            yield k, v

    def _pvgroup(config):
        return PKDict(
            # Need to hardwire the defaults, because ioc_arg_parser uses
            # argparse globally which causes a mess with argh (which uses argparse)
            pvdb=_PVGroup(config, db_yaml, macros={}, prefix="").pvdb,
            interfaces=["0.0.0.0"],
            module_name="caproto.asyncio.server",
            log_pv_names=False,
        )

    caproto.server.run(**_pvgroup(PKDict(_normalize(_fconf()))))


class _PVGroup(caproto.server.PVGroup):

    def __init__(self, config, db_yaml, *args, **kwargs):
        self.__config = config
        self.__db_yaml = pykern.pkio.py_path(db_yaml) if db_yaml else None
        self.__db = PKDict()
        for k, v in self.__config.items():
            self._pvs_[k] = p = caproto.server.pvproperty(value=v.value)
            self.__db[k] = v.value
            p.__set_name__(self, k)
        self.__write_db()
        super().__init__(*args, **kwargs)

    async def group_write(self, instance, value, **kwargs):
        async def _dispatch(todo):
            for k, v in todo.items():
                u = _un_numpy(v[value], k)
                if self.__db[k] != u:
                    self.__db[k] = u
                    await self.pvdb[k].write(u)

        def _un_numpy(v, name):
            if not isinstance(v, numpy.generic):
                return v
            if isinstance(v, numpy.integer):
                return int(v)
            if isinstance(v, numpy.floating):
                return float(v)
            if isinstance(v, numpy.bool_):
                return bool(v)
            raise AssertionError(f"unhandled type={type(v)} pv={name}")

        try:
            if self.__db[instance.pvname] != value:
                self.__db[instance.pvname] = _un_numpy(value, instance.pvname)
                await _dispatch(self.__config[instance.pvname].dispatch)
                self.__write_db()
            return await super().group_write(instance, value, **kwargs)
        except Exception as e:
            pkdlog(
                "error={} pv={} value={} stack={}", e, instance.name, value, pkdexc()
            )
            raise

    def __write_db(self):
        if self.__db_yaml:
            pykern.pkio.atomic_write(
                self.__db_yaml,
                writer=lambda p: pykern.pkyaml.dump_pretty(self.__db, filename=p),
            )
