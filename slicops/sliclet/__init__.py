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
    # sort in priority value order, lowest number is highest priority
    error = 1
    session_end = 2
    ctx_write = 3


_HANDLE_CTX_SET_RE = re.compile("^handle_ctx_set_(\w+)$")

_CTX_WRITE_ARGS = frozenset(["field_values"])


def instance(name, queue):
    return importlib.import_module(f"slicops.sliclet.{name}").CLASS(name, queue)


class Base:
    def __init__(self, name, ctx_update_q):
        self.__name = name
        self.__loop = asyncio.get_event_loop()
        self.__ctx_update_q = ctx_update_q
        # This might fail due to errors in the yaml
        self.__locked = False
        self.__ctx = slicops.ctx.Ctx(self.__name)
        self.__work_q = queue.PriorityQueue()
        self.__lock = threading.RLock()
        self.__ctx_set_handlers = PKDict(self.__inspect_ctx_set_handlers())
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

    def handle_start(self, txn):
        pass

    @contextlib.contextmanager
    def lock_for_update(self, log_op=None, _first_time=False):
        ok = True
        try:
            with self.__lock:
                if self.__locked:
                    ok = False
                    raise AssertionError("may only lock once")
                txn = None
                try:
                    self.__locked = True
                    txn = slicops.ctx.Txn(self.__ctx, first_time=_first_time)
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
            d = f"error={e}"
            try:
                if not log_op:
                    log_op = pykern.pkinspect.caller()
                d += f" op={log_op}"
            except Exception as e2:
                pkdlog("error={} during exception stack={}", e2, pkdexc())
            if not isinstance(e, pykern.util.APIError):
                pkdlog("stack={}", pkdexc())
            pkdlog("ERROR {}", d)
            self.__put_work(_Work.error, PKDict(desc=d))

    def session_end(self):
        self.__put_work(_Work.session_end, None)

    def __inspect_ctx_set_handlers(self):
        for n, o in inspect.getmembers(self):
            if (m := _HANDLE_CTX_SET_RE.search(n)) and inspect.ismethod(o):
                yield m.group(1), o

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
            #TODO(robnagler) may not want all these to be None
            self.__ctx_update_q = None
            self.__work_q = None
            self.__thread = None
            self.__lock = None

        try:
            with self.lock_for_update(_first_time=True) as txn:
                self.handle_start(txn=txn)
            while True:
                w = a = None
                try:
                    w, a = self.__work_q.get()
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
            except Exception:
                pass
        finally:
            _destroy()

    def __ctx_update(self, result):
        self.__loop.call_soon_threadsafe(self.__ctx_update_q.put_nowait, result)

    def _work_error(self, msg):
        self.__ctx_update(pykern.util.APIError("{}", msg))
        return False

    def _work_session_end(self, unused):
        # TODO(robnagler) maybe if there are too many errors fail or stop logging?
        return False

    def _work_ctx_write(self, field_values):
        with self.lock_for_update(log_op="ctx_write") as txn:
            for c in tuple(txn.field_set_via_api(*x) for x in field_values.items()):
                if a := self.__ctx_set_handlers.get(c.field):
                    a(txn=txn, **c)
        return True
