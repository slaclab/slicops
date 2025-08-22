"""Support for unit tests

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

# limit imports that might touch config
import asyncio
import pykern.api.unit_util
import contextlib

# TODO(robnagler) configurable?
_TIMEOUT = 2


class SlicletSetup(pykern.api.unit_util.Setup):
    def __init__(self, sliclet, *args, **kwargs):
        self.__sliclet = sliclet
        super().__init__(*args, **kwargs)
        self.__update_q = asyncio.Queue()

    async def ctx_update(self):
        from pykern import pkunit

        self.__caller()
        r = await asyncio.wait_for(self.__update_q.get(), timeout=_TIMEOUT)
        self.__update_q.task_done()
        if r is None:
            pkunit.pkfail("subscription ended unexpectedly")
        return r

    async def ctx_field_set(self, **kwargs):
        from pykern.pkcollections import PKDict
        from pykern import pkdebug

        self.__caller()
        await self.client.call_api("ui_ctx_write", PKDict(field_values=PKDict(kwargs)))

    async def __aenter__(self):
        await super().__aenter__()
        asyncio.create_task(self.__subscribe())
        return self

    def _global_config(self, **kwargs):
        from pykern import util

        return super()._global_config(
            SLICOPS_CONFIG_UI_API_TCP_PORT=str(util.unbound_localhost_tcp_port()),
            **kwargs,
        )

    def _http_config(self, *args, **kwargs):
        from slicops import config

        return config.cfg().ui_api.copy()

    def _server_config(self, *args, **kwargs):
        return super()._server_config(*args, **kwargs)

    def _server_start(self, *args, **kwargs):
        from slicops.pkcli import service

        service.Commands().ui_api()

    def __caller(self):
        from pykern import pkdebug, pkinspect
        import inspect, re

        c = str(pkinspect.caller())
        if m := re.search("^.*/(.+)", c):
            c = m.group(1)
        pkdebug.pkdlog("{} op={}", c, pkinspect.caller_func_name())

    async def __subscribe(self):
        from pykern import pkdebug
        from pykern.pkcollections import PKDict
        from pykern.api import util

        try:
            with await self.client.subscribe_api(
                "ui_ctx_update", PKDict(sliclet=self.__sliclet)
            ) as s:
                while True:
                    r = await asyncio.wait_for(s.result_get(), timeout=_TIMEOUT)
                    self.__update_q.put_nowait(r)
                    if r is None:
                        return
        except util.APIDisconnected:
            pkdebug.pkdlog("APIDisconnected sliclet={}", self.__sliclet)
        except Exception as e:
            pkdebug.pkdlog("error={} stack={}", e, pkdebug.pkdexc())
            raise
        finally:
            pkdebug.pkdlog("ui_ctx_update subscription ended normally")


@contextlib.contextmanager
def random_epics_ports():
    """Open the IOC"""

    from pykern import util, pkconst
    import os
    import socket

    r = str(util.unbound_localhost_udp_port())
    s = str(util.unbound_localhost_udp_port())
    os.environ.update(
        dict(
            EPICS_CAS_AUTO_BEACON_ADDR_LIST="no",
            EPICS_CAS_BEACON_ADDR_LIST=pkconst.LOCALHOST_IP,
            EPICS_CAS_BEACON_PORT=r,
            EPICS_CAS_INTF_ADDR_LIST=pkconst.LOCALHOST_IP,
            EPICS_CAS_SERVER_PORT=s,
            EPICS_CA_ADDR_LIST=pkconst.LOCALHOST_IP,
            EPICS_CA_AUTO_ADDR_LIST="no",
            EPICS_CA_REPEATER_PORT=r,
            EPICS_CA_SERVER_PORT=s,
        )
    )
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", int(r)))
        yield None


@contextlib.contextmanager
def setup_screen(beam_path, device_name):
    with start_ioc("ioc.yaml"):
        from slicops.device import screen
        from pykern.pkcollections import PKDict

        rv = PKDict(handler=_screen_handler())
        rv.device = screen.Screen(beam_path, device_name, rv.handler)
        try:
            yield rv
        finally:
            rv.device.destroy()


@contextlib.contextmanager
def start_ioc(init_yaml, db_yaml=None):
    import os, signal, time
    import socket

    def _path(path, arg):
        return path.join(arg) if isinstance(arg, str) else arg

    with random_epics_ports():
        p = os.fork()
        if p == 0:
            from pykern import pkdebug

            try:
                from slicops.pkcli import ioc
                from pykern import pkunit

                ioc.run(
                    _path(pkunit.data_dir(), init_yaml),
                    db_yaml=_path(pkunit.work_dir(), db_yaml),
                )
            except Exception as e:
                pkdebug.pkdlog("server exception={} stack={}", e, pkdebug.pkdexc())
            finally:
                os._exit(0)
        try:
            time.sleep(1)
            yield None
        finally:
            os.kill(p, signal.SIGKILL)


def _screen_handler():
    from pykern import pkunit
    from pykern.pkcollections import PKDict
    import queue
    from slicops.device import screen

    class _Handler(screen.EventHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.event_q = PKDict(
                {
                    k: queue.Queue()
                    for k in ("acquire", "image", "target_status", "error")
                }
            )

        def on_screen_device_error(self, **kwargs):
            self.event_q.error.put_nowait(PKDict(kwargs))

        def on_screen_device_update(self, **kwargs):
            self.event_q[kwargs["accessor_name"]].put_nowait(PKDict(kwargs))

        def test_get(self, event_name):
            try:
                rv = self.event_q[event_name].get(timeout=_TIMEOUT)
                # Errors don't have value
                return rv.get("value", rv)
            except queue.Empty:
                pkunit.pkfail("timeout event={}", event_name)

    return _Handler()
