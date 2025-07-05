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
            self.__db_watcher.destroy()
            self.__db_watcher = None

    def thread_run_start(self):
        self.__db_watcher = _DBWatcher(self._db_watcher_update)

    def ui_action_save_button(self, txn):
        def _values():
            for k in self.__writable_keys(txn):
                yield k, txn.field_get(k)

        # TODO(robnagler) work item maybe should happen outside ui_action()
        #    work_queue is a separate thing that could be queued
        slicops.pkcli.simple.write(PKDict(_values()))

    def ui_action_revert_button(self, txn):
        # TODO(robnagler) the read and the ctx_put could happen outside the context
        return self.__read_db(txn)

    def __db_watcher_update(self):
        with self.lock_for_update() as txn:
            self.__read_db(txn)

    def __read_db(self, txn):
        try:
            d = slicops.pkcli.simple.read()
        except Exception as e:
            # Db may not exist
            if pykern.pkio.exception_is_not_found(e):
                return
            raise
        for k in self.__writable_keys(txn):
            if k in d:
                txn.field_set(k, d[k])

    def __writable_keys(self, txn):
        for k in txn.field_names():
            if txn.ui_get(k, "writable"):
                yield k


CLASS = Simple


class _DBWatcher(watchdog.events.FileSystemEventHandler):
    def __init__(self, update_op):
        super().__init__()
        self.__update_op = update_op
        p = slicops.pkcli.simple.path()
        self.__path = str(p)
        self.__observer = watchdog.observers.Observer()
        self.__observer.schedule(self, p.dirname, recursive=False)
        self.__observer.start()

    def on_any_event(self, event):
        if event.event_type in _EVENT_TYPES and (
            self.__path == event.src_path or self.__path == event.dest_path
        ):
            self.__update_op()

    def destroy(self):
        if self.__observer:
            o = self.__observer
            self.__observer = None
            o.stop()
