"""Base for sliclets

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp, pkdformat
import asyncio
import contextlib
import enum
import importlib
import inspect
import pykern.util
import queue
import re
import slicops.ctx
import slicops.field
import threading


class _Work(enum.IntEnum):
    error = 1
    session_end = 2
    ctx_write = 3
    start = 4


_ON_METHODS_RE = re.compile(r"^on_(click|change)_(\w+)$")

_CTX_WRITE_ARGS = frozenset(["field_values"])


def instance(name, queue):
    if not name:
        name = _cfg.default
    return importlib.import_module(f"slicops.sliclet.{name}").CLASS(name, queue)


class Base:
    def __init__(self, name, ctx_update_q):
        self.name = name
        self.title = self.__class__.__name__
        self.__loop = asyncio.get_event_loop()
        self.__ctx_update_q = ctx_update_q
        # This might fail due to errors in the yaml
        self.__locked = False
        self.__ctx = slicops.ctx.Ctx(self.name, self.title)
        self.__work_q = queue.Queue()
        self.__lock = threading.RLock()
        self.__on_methods = self.__inspect_on_methods()
        txn = slicops.ctx.Txn(self.__ctx)
        self.handle_init(txn)
        txn.commit(None)
        self.__ctx_update(self.__ctx.first_time())
        self.__put_work(_Work.start, None)
        self.__thread = threading.Thread(target=self.__run, daemon=True)
        self.__thread.start()

    def ctx_write(self, field_values):
        for k, v in field_values.items():
            if not (f := self.__ctx.fields.get(k)):
                raise pykern.util.APIError("unknown field={}", k)
            # This is pre-emptive so errors make sense in context of write
            if isinstance((v := f.value_check(v)), slicops.field.InvalidFieldValue):
                raise pykern.util.APIError("invalid value for field={} error={}", k, v)
        self.__put_work(_Work.ctx_write, field_values)

    def handle_destroy(self):
        pass

    def handle_init(self, txn):
        pass

    def handle_start(self, txn):
        pass

    @contextlib.contextmanager
    def lock_for_update(self, log_op=None):
        ok = True
        try:
            with self.__lock:
                if self.__locked:
                    ok = False
                    raise AssertionError("may only lock once")
                txn = None
                try:
                    self.__locked = True
                    txn = slicops.ctx.Txn(self.__ctx)
                    yield txn
                except Exception:
                    if txn:
                        txn.rollback()
                    raise
                else:
                    txn.commit(self.__ctx_update)
                finally:
                    self.__locked = False
        except Exception as e:
            if not ok:
                raise
            if not (d := str(e)):
                d = str(type(e))
            d = f"error={d}"
            try:
                if log_op:
                    d += f" op={log_op}"
            except Exception as e2:
                pkdlog("error={} during exception stack={}", e2, pkdexc())
            if not isinstance(e, pykern.util.APIError):
                pkdlog("stack={}", pkdexc())
            pkdlog("ERROR {}", d)
            self.__put_work(_Work.error, PKDict(desc=d))

    def session_end(self):
        self.__put_work(_Work.session_end, None)

    def __inspect_on_methods(self):
        rv = PKDict()
        for k, v in inspect.getmembers(self):
            if (m := _ON_METHODS_RE.search(k)) and inspect.ismethod(v):
                if m.group(2) in rv:
                    raise AssertionError(
                        f"only one of on_click or on_change field={m.group(2)}"
                    )
                rv[m.group(2)] = PKDict(kind=m.group(1), func=v)
        return rv

    def __put_work(self, work, arg):
        self.__work_q.put_nowait((work, arg))

    def __run(self):
        def _destroy():
            try:
                self.handle_destroy()
            except Exception:
                pass
            try:
                # Try to end session. Might already be ended
                self.__loop.call_soon_threadsafe(self.__ctx_update_q.put_nowait, None)
            except Exception:
                pass

        try:
            while True:
                w = a = None
                try:
                    w, a = self.__work_q.get()
                    self.__work_q.task_done()
                    if not getattr(self, f"_work_{w._name_}")(a):
                        return
                except Exception as e:
                    pkdlog("{}={} error={} stack={}", w, a, e, pkdexc())
                    if w == _Work.error:
                        pkdlog("error during error handling error={}", e)
                        return
                    self.__put_work(_Work.error, f"error={e} op={w}")
        except Exception as e:
            try:
                pkdlog("error={} stack={}", e, pkdexc())
                self._work_error(e)
            except Exception:
                pass
        finally:
            _destroy()

    def __ctx_update(self, result):
        self.__loop.call_soon_threadsafe(self.__ctx_update_q.put_nowait, result)

    def _work_error(self, msg):
        self.__ctx_update(
            msg
            if isinstance(msg, pykern.util.APIError)
            else pykern.util.APIError("{}", msg)
        )
        return False

    def _work_ctx_write(self, field_values):
        def _change(updates):
            for u in updates:
                if u.on_method.kind == "change":
                    u.pkdel("on_method").func(**u)
                else:
                    yield u

        def _click(updates):
            for u in updates:
                u.pkdel("on_method").func(**u)

        def _updates():
            m = self.__on_methods
            for k, v in field_values.items():
                if c := txn.field_set_via_api(k, v, m.get(k)):
                    yield c

        with self.lock_for_update(log_op="ctx_write") as txn:
            _click(tuple(_change(sorted(_updates(), key=lambda x: x.field_name))))
        return True

    def _work_session_end(self, unused):
        # TODO(robnagler) maybe if there are too many errors fail or stop logging?
        return False

    def _work_start(self, unused):
        with self.lock_for_update(log_op="start") as txn:
            self.handle_start(txn=txn)
        return True


def _init():
    global _cfg
    from pykern import pkconfig

    _cfg = pkconfig.init(
        default=("screen", str, "default sliclet"),
    )


_init()
