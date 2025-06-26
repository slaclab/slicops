"""Simple file based Sliclet

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import slicops.sliclet
import pykern.pkio
import slicops.pkcli.simple
import watchdog.events
import watchdog.observers

_EVENT_TYPES = frozenset(
    (
        watchdog.events.EVENT_TYPE_MOVED,
        watchdog.events.EVENT_TYPE_CREATED,
        watchdog.events.EVENT_TYPE_MODIFIED,
    ),
)


class Simple(slicops.sliclet.Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__db_watcher = None

    def destroy(self):
        if self.__db_watcher:
            x = self.__db_watcher
            self.__db_watcher = x
            x.destroy()

    def thread_run_start(self):
        self.__db_watcher = _DBWatcher(self)

    def ui_action_save_button(self, value):
        def _values():
            c = self.ctx
            t = c.get_class("Button")
            return ((f.name, f.value) for f in c.values() if not isinstance(f, t))

        slicops.pkcli.simple.write(PKDict(_values()))

    def ui_action_revert_button(self, value):
        self._read_db()

    def _db_watcher_update(self):
        try:
            self._read_db()
        except Exception as e:
            self.thread_exception("reading database", e)

    def _read_db(self):
        try:
            d = slicops.pkcli.simple.read()
        except Exception as e:
            # Db may not exist
            if pykern.pkio.exception_is_not_found(e):
                return
            raise
        self.update_fields(PKDict((k, db[k]) for k in self.field_names()))


CLASS = Simple


class _DBWatcher(watchdog.events.FileSystemEventHandler):
    def __init__(self, sliclet):
        super().__init__()
        self.__sliclet = sliclet
        p = slicops.pkcli.simple.path()
        self.__path = str(p)
        self.__observer = watchdog.observers.Observer()
        self.__observer.schedule(self, p.dirname, recursive=False)
        self.__observer.start()

    def on_any_event(self, event):
        if event.event_type in _EVENT_TYPES and (
            self.__path == event.src_path or self.__path == event.dest_path
        ):
            self.sliclet._db_watcher_update()

    def destroy(self):
        if self.__observer:
            o = self.__observer
            self.__observer = None
            o.stop()
