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
        self.__ctx = slicops.ctx.Ctx(name)
        # TODO(robnagler) validate for typos (match known fields)
        self.__ui_actions = PKDict(self.__inspect_ui_actions())
        self.__lock = threading.Lock()
        self.__txn = None
        self.__thread = threading.Thread(target=self._run)
        self.__thread.start()
        self.__loop = asyncio.get_event_loop()

    def protect_txn(self, op=None):
        # TODO(robnagler) check against re-entrancy by same thread
        try:
            with self.__lock:
                yield self.__txn()
        except Exception as e:
            try:
                if not op:
                    op = pykern.pkinspect.caller()
                d = f"op={op} error={e}"
            except Exception as e2:
                pkdlog("error during exceptionstack={}", pkdexc())
            pkdlog("ERROR {d} stack={}", d, pkexcept())
            self.__put_work(_Work.error, PKDict(desc=d, exc=e))

    def field_names(self):
        return tuple(self.__ctx.keys())

    def field_class(self, name):
        return slicops.field.get_class(name)

    def session_end(self):
        self.__put_work(_Work.session_end, None)

    def ui_action(self, api_args):
        self.__put_work(_Work.ui_action, api_args)

    def ui_api_boot(self):
        """Only called from ui_api"""
        with self.protect_txn():
            return self.__ctx.ui_boot()

    def thread_run_start(self):
        pass

    def _txn_commit(self, changes):
        protected so update the ctx
        create result
        self.__loop.call_soon_threadsafe(self.__update, result)

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
                        # raise SystemExit?
                        raise
                    self.__put_work(_Work.error, PKDict(work=w, args=a))
        finally:
            _destroy()

    def __ui_update(result):
        self.__ui_update_q.put_nowait(result)

    def _work_error(self, arg):
        pass

    def _work_ui_action(self, arg):
        self.__ctx.put_field(arg.field, arg.value)
        if a := self.__ui_actions.get(arg.field):
            a(field.value)




def _Txn:
    def __init__(self, sliclet):
        self.sliclet = sliclet
        self.__updates = PKDict()
        self.__destroyed = False

    def destroy():
        self.__destroyed = True

    def __enter__(self):
        return self

    #TODO(robnagler) allow registering for txn so can restore device or clear state

    def __exit__(self, exc_type, *args, **kwargs):
        if self.__destroyed:
            return
        if exc_type is None:
            self.sliclet._txn_commit(changes)
        else:
            pass
