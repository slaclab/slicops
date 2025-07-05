"""Base for sliclets

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
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
    # sort in value order
    error = (1,)
    session_end = (2,)
    ui_field_change = (3,)


_UI_FIELD_CHANGE_RE = re.compile("^ui_field_change_(\w+)$")

_UI_FIELD_CHANGE_ARGS = frozenset(("field", "value"))


def instance(name, queue):
    return importlib.import_module(f"slicops.sliclet.{name}").CLASS(name, queue)


class Base:
    def __init__(self, name, ui_ctx_update_q):
        self.__name = name
        self.__ui_ctx_update_q = ui_ctx_update_q
        self.__loop = asyncio.get_event_loop()
        self.__thread = threading.Thread(target=self._run, daemon=True)
        self.__thread.start()

    @contextlib.contextmanager
    def lock_for_update(self, log_op=None):
        ok = True
        try:
            with self.__lock:
                if self.__locked:
                    ok = False
                    raise AssertionError("may only lock once")
                t = None
                try:
                    self.__locked = True
                    t = _Txn(self.__ctx)
                    yield t
                except Exception:
                    if t:
                        t.rollback()
                else:
                    t.commit(self.__ui_ctx_update)
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
            pkdlog("ERROR {} stack={}", d, pkdexc())
            self.__put_work(_Work.error, PKDict(desc=d))

    def session_end(self):
        self.__put_work(_Work.session_end, None)

    def thread_run_start(self):
        pass

    def ui_field_change(self, api_args):
        if (x := set(api_args.keys())) != _UI_FIELD_CHANGE_ARGS:
            raise pykern.util.APIError("invalid ui_field_change api_args={x}")
        self.__put_work(_Work.ui_field_change, api_args)
        return PKDict()

    def __init_rest(self):
        self.__work_q = queue.PriorityQueue()
        self.__lock = threading.RLock()
        self.__locked = False
        self.__ui_field_changes = PKDict(self.__inspect_ui_field_changes())
        self.__ctx = slicops.ctx.Ctx(self.__name)
        self.__ui_ctx_update(self.__ctx.as_api_result())

    def __inspect_ui_field_changes(self):
        for n, o in inspect.getmembers(self):
            if (m := _UI_FIELD_CHANGE_RE.search(n)) and inspect.isfunction(o):
                yield m.group(1), o

    def __put_work(self, work, arg):
        self.__work_q.put_nowait((work, arg))

    def _run(self):
        def _destroy():
            try:
                # Try to end session. Might already be ended
                self.__loop.call_soon_threadsafe(
                    self.__ui_ctx_update_q.put_nowait, None
                )
            except:
                pass
            self.__ui_ctx_update_q = None
            self.__work_q = None
            self.__thread = None
            self.__lock = None
            if self.__txn:
                try:
                    self.__txn.rollback()
                except Exception:
                    pass
                self.__txn = None

        try:
            self.__init_rest()
            self.thread_run_start()
            while True:
                w = a = None
                try:
                    w, a = self.__work_q.get()
                    if not getattr(self, f"_work_{w._name_}")(a):
                        return
                except Exception as e:
                    pkdlog("{}={} error={} stack={}", w, a, e, pkdexc())
                    if w == _Work.error:
                        pkdlog("error during error handling")
                        return
                    self.__put_work(_Work.error, f"error={e} op={w}")
        except Exception as e:
            pkdlog("error={} stack={}", e, pkdexc())
        finally:
            _destroy()

    def __ui_ctx_update(self, result):
        self.__loop.call_soon_threadsafe(self.__ui_ctx_update_q.put_nowait, result)

    def _work_error(self, msg):
        self.__ui_ctx_update(pykern.util.APIError("{}", msg))
        return False

    def _work_session_end(self, unused):
        # TODO(robnagler) maybe if there are too many errors fail or stop logging?
        return False

    def _work_ui_field_change(self, arg):
        with self.lock_for_update(log_op=f"ui_field_change_{arg.field}") as txn:
            x = txn.field_set(arg.field, arg.value)
            if a := self.__ui_field_changes.get(arg.field):
                a(txn, **x)
        return True


class _Txn:
    def __init__(self, ctx):
        self.__ctx = ctx
        self.__updates = PKDict(ctx=PKDict())
        self.__destroyed = False

    def commit(self, update):
        if self.__destroyed:
            return
        if self.__updates.ctx:
            # Only send if there are changes
            update(self.__updates)
        self.__updates = None

    def field_get(self, name):
        return self.__ctx.fields[name].value_get()

    def field_names(self):
        # might be used outside of txn
        return tuple(self.__ctx.fields.keys())

    def field_set(self, name, value):
        p = ctx.fields[name].value_get()
        # TODO(robnagler) rollback
        rv = PKDict(value=ctx.fields[name].value_set(value))
        rv.changed = rv.value != p
        if rv.changed:
            self.__updates.ctx.pksetdefault1(name, PKDict).value = rv.value
        # assumes caller will not modify value
        return rv

    def rollback(self):
        self.__updates = None

    def ui_get(self, field, attr):
        return self.__ctx.fields[field].ui_get(attr)
