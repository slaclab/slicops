"""Simple file based Sliclet

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import slicops.sliclet
import pykern.pkio
import slicops.pkcli.simple
import slicops.pkcli.fractals
import watchdog.events
import watchdog.observers

_EVENT_TYPES = frozenset(
    (
        watchdog.events.EVENT_TYPE_MOVED,
        watchdog.events.EVENT_TYPE_CREATED,
        watchdog.events.EVENT_TYPE_MODIFIED,
    ),
)


# TODO(robnagler) Rename to yaml_db and Simple would inherit from it
class Simple(slicops.sliclet.Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__db_watcher = None

    def handle_destroy(self):
        # TODO(robnagler) Need to make idempotent
        if self.__db_watcher:
            self.__db_watcher.destroy()
            self.__db_watcher = None

    def handle_start(self, txn):
        # TODO(robnagler) need a separate init for the instance before start
        self.__base = self.__class__.__name__.lower()
        self.__db_cache = PKDict()
        if not self.__read_db(txn):
            self.__write(txn)
        self.__db_watcher = _DBWatcher(
            (
                slicops.pkcli.simple.path(self.__base),
                slicops.pkcli.fractals.path(),
            ),
            self.__db_watcher_update,
        )

    def handle_ctx_set_save(self, txn, **kwargs):
        self.__write(txn)

    def handle_ctx_set_revert(self, txn, **kwargs):
        # TODO(robnagler) the read and the ctx_put could happen outside the context
        self.__read_db(txn)

    def __db_watcher_update(self):
        if not self.__db_watcher_update:
            # destroyed
            return
        with self.lock_for_update() as txn:
            self.__read_db(txn)

    def __read_db(self, txn):
        def _keys():
            for k in txn.field_names():
                if txn.ui_get(k, "widget") not in (
                    "button",
                    "heatmap",
                    "heatmap_with_lineouts",
                ):
                    yield k

        if not (r := slicops.pkcli.simple.read(self.__base)):
            return False
        for k in _keys():
            if k in r and r[k] != self.__db_cache.get(k):
                txn.field_set(k, r[k])
        self.__db_cache = r
        if "plot_file" in txn.field_names() and "plot" in txn.field_names():
            import numpy

            txn.multi_set(("plot.ui.visible", False))
            txn.field_set("plot", PKDict(raw_pixels=None))
            try:
                txn.field_set(
                    "plot",
                    PKDict(raw_pixels=numpy.load(txn.field_get("plot_file"))),
                )
                txn.multi_set(("plot.ui.visible", True))
            except Exception as e:
                pkdlog("{} {}", e, pkdexc())
        return True

    def __write(self, txn):
        def _keys():
            for k in txn.field_names():
                if txn.ui_get(k, "writable") and txn.ui_get(k, "widget") not in (
                    "button",
                    "heatmap",
                    "heatmap_with_lineouts",
                ):
                    yield k

        def _values():
            for k in _keys():
                yield k, txn.field_get(k)

        # TODO(robnagler) work item maybe should happen outside handle_ctx_set
        #    work_queue is a separate thing that could be queued
        self.__db_cache = PKDict(_values())
        slicops.pkcli.simple.write(self.__base, self.__db_cache)


CLASS = Simple


class _DBWatcher(watchdog.events.FileSystemEventHandler):
    def __init__(self, paths, update_op):
        super().__init__()
        self.__update_op = update_op
        self.__paths = str(paths)
        self.__observer = watchdog.observers.Observer()
        self.__observer.schedule(self, paths[0].dirname, recursive=False)
        self.__observer.start()

    def on_any_event(self, event):
        if event.event_type in _EVENT_TYPES and (
            event.src_path in self.__paths or event.dest_path in self.__paths
        ):
            self.__update_op()

    def destroy(self):
        if self.__observer:
            o = self.__observer
            self.__observer = None
            o.stop()
