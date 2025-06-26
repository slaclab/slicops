"""Base for sliclets

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import slicops.field
import slicops.ctx
import queue
import threading
import re


class _Work(enum.IntEnum):
    # sort in value order
    error = (1,)
    session_end = (2,)
    update = (3,)
    ui_action = (4,)


_UI_ACTION_RE = re.compile("^ui_action_(\w+)$")


def instance(name, queue):
    importlib.import_module(f"slicops.sliclet.{name}").CLASS(name, queue)


class Base:
    def __init__(self, name, ui_update_queue):
        super().__init__(daemon=True)
        self.__name = name
        self.__ui_update_queue = ui_update_queue
        self.__work_queue = queue.PriorityQueue()
        self.__ctx = slicops.ctx.Ctx(name)
        # TODO(robnagler) validate for typos (match known fields)
        self.__ui_actions = PKDict(self.__inspect_ui_actions())
        self.__thread = threading.Thread(target=self._run)
        self.__thread.start()

    def field_names(self):
        return tuple(self.__ctx.keys())

    def field_class(self, name):
        return slicops.field.get_class(name)

    def session_end(self):
        self.__put_work(_Work.session_end, None)

    def thread_exception(self, desc, exc):
        pkdlog("{} error={} stack={}", self._name, exc)
        self.__put_work(_Work.error, PKDict(desc=desc, exc=exc))

    def ui_action(self, api_args):
        self.__put_work(_Work.ui_action, api_args)

    def ui_boot(self):
        return self.__ctx.ui_boot()

    def thread_run_start(self):
        pass

    def __inspect_ui_actions(self):
        for n, o in inspect.members(self):
            if (m := _UI_ACTION_RE.search(n)) and inspect.isfunction(o):
                yield m.group(1), o

    def __put_work(self, work, arg):

        self.__work_queue.put_nowait(work, arg)

    def _run(self):
        def _destroy():
            self.__session = None
            self.__update_queue = None
            self.__work_queue = None
            self.__thread = None

        try:
            self.thread_run_start()
            while True:
                w, a = self.__work_queue.get()
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

    def _work_error(self, arg):
        pass

    def _work_ui_action(self, arg):
        self.__ctx.put_field(arg.field, arg.value)
        if a := self.__ui_actions.get(arg.field):
            a(field.value)
