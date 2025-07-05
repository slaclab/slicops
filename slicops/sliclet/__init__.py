"""Base for sliclets

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import asyncio
import queue
import re
import slicops.ctx
import slicops.field
import threading


class _Work(enum.IntEnum):
    # sort in value order
    error = (1,)
    session_end = (2,)
    ui_action = (3,)


_UI_ACTION_RE = re.compile("^ui_action_(\w+)$")


def instance(name, queue):
    importlib.import_module(f"slicops.sliclet.{name}").CLASS(name, queue)


class Base:
    def __init__(self, name, ui_update_q):
        super().__init__(daemon=True)
        self.__name = name
        self.__ui_update_q = ui_update_q
        self.__work_q = queue.PriorityQueue()
        # TODO(robnagler) validate for typos (match known fields)
        self.__ui_actions = PKDict(self.__inspect_ui_actions())
        self.__lock = threading.RLock()
        self.__locked = False
        self.__thread = threading.Thread(target=self._run)
        self.__thread.start()
        self.__loop = asyncio.get_event_loop()

        rjn ctx parsing gets an error
        self.__ctx = slicops.ctx.Ctx(name)
        rjn queue first update

    def lock_for_update(self, log_op=None):
        # TODO(robnagler) check against re-entrancy by same thread
        ok = True
        try:
            with self.__lock:
                self.__assert_not_destroyed()
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
                    t.commit(self.__ui_update)
                finally:
                    self.__locked = False
        except Exception as e:
            if not ok:
                raise
            try:
                if not log_op:
                    log_op = pykern.pkinspect.caller()
                d = f"op={log_op} error={e}"
            except Exception as e2:
                pkdlog("error={} during exception stack={}", e2, pkdexc())
            pkdlog("ERROR {d} stack={}", d, pkdexc())
            self.__put_work(_Work.error, PKDict(desc=d))

    def session_end(self):
        self.__put_work(_Work.session_end, None)

    def thread_run_start(self):
        pass

    def ui_action(self, api_args):
        self.__put_work(_Work.ui_action, api_args)

    def __assert_not_destroyed(self):
        if self.__destroyed:
            pass

    def __inspect_ui_actions(self):
        for n, o in inspect.members(self):
            if (m := _UI_ACTION_RE.search(n)) and inspect.isfunction(o):
                yield m.group(1), o

    def __put_work(self, work, arg):
        self.__work_q.put_nowait(work, arg)

    def _run(self):
        def _destroy():
            self.__session = None
            self.__ui_update_q = None
            self.__work_q = None
            self.__thread = None
            self.__lock = None
            if self.__txn:
                self.__txn.destroy()
                self.__txn = None

        try:
            self.thread_run_start()
            while True:
                w, a = self.__work_q.get()
                if w == _Work.session_end:
                    self.destroy()
                    return
                try:
                    getattr(self, f"_work_{w._name_}")(a)
                except Exception as e:
                    pkdlog("{}={} error={} stack={}", w, a, e, pkdexc())
                    if w == _Work.error:
                        error during work
                        # raise SystemExit?
                        raise
                    self.__put_work(_Work.error, e)
        finally:
            _destroy()

    def __ui_update(self, result):
        self.__loop.call_soon_threadsafe(self.__ui_update_q.put_nowait, result)

    def _work_error(self, exc):
        # TODO(robnagler) maybe if there are too many errors fail or stop logging?
        self.__ui_update(exc)

    def _work_ui_action(self, arg):
        with self.lock_for_update() as txn:
            txn.field_set(arg.field, arg.value)
            if a := self.__ui_actions.get(arg.field):
                a(field.value)


class _Txn:
    def __init__(self, ctx):
        self.__ctx = ctx
        self.__updates = PKDict(ctx=PKDict(), ui_layout=PKDict())
        self.__destroyed = False

    def commit(self, update):
        update(self.__updates)
        self.destroy()

    def destroy():
        self.__destroyed = True
        self.__updates = None

    def field_get(self, name):
        return self.__ctx.fields[name].value_get()

    def field_names(self):
        return self.__ctx.fields.keys()

    def field_set(self, name, value):
        pkdp("need to be able to shadow")
        self.__updates.ctx.pksetdefault1(name, PKDict).value = rv = ctx.fields[
            name
        ].value_set(value)
        return rv

    def rollback(self):
        self.destroy()

    def ui_get(self, field, name):
        return self.__ctx.fields[field].ui_get(name)
