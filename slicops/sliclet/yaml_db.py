"""YAML Db Sliclet

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import numpy
import pykern.pkio
import slicops.pkcli.fractals
import slicops.pkcli.yaml_db
import slicops.sliclet
import watchdog.events
import watchdog.observers
import watchdog.observers.polling


_EVENT_TYPES = frozenset(
    (
        watchdog.events.EVENT_TYPE_MOVED,
        watchdog.events.EVENT_TYPE_CREATED,
        watchdog.events.EVENT_TYPE_MODIFIED,
    ),
)


class YAMLDb(slicops.sliclet.Base):
    def handle_destroy(self):
        # TODO(robnagler) Need to make idempotent
        if self.__db_watcher:
            self.__db_watcher.destroy()
            self.__db_watcher = None

    def handle_init(self, txn):
        self.__db_watcher = None

    def handle_start(self, txn):
        # TODO(robnagler) need a separate init for the instance before start
        self.__db_cache = PKDict()
        if not self.__read_db(txn):
            self.__write(txn)
        self.__db_watcher = _DBWatcher(
            (
                slicops.pkcli.yaml_db.path(self.name),
                slicops.pkcli.fractals.path(),
            ),
            self.__db_watcher_update,
        )

    def on_click_save(self, txn, **kwargs):
        self.__write(txn)

    def on_click_revert(self, txn, **kwargs):
        # TODO(robnagler) the read and the ctx_put could happen outside the context
        self.__db_cache = PKDict()
        self.__read_db(txn)

    def __db_watcher_update(self):
        if not self.__db_watcher_update:
            # destroyed
            return
        with self.lock_for_update() as txn:
            self.__read_db(txn)

    # TODO(robnagler) can this be encapsulated in a base prototype?
    # field.new would need to evaluate in a particular order.
    # Perhaps there should be "related:" color_map, numpy_file_field, etc.
    def __numpy_file(self, txn, plot, links):
        def _visibility(value):
            yield (f"{plot}.ui.visible", value)
            if x := links.get("color_map"):
                yield (f"{x}.ui.visible", value)

        if not (n := links.get("numpy_file")):
            # Not numpy field
            return None
        # Set plot always, and raw_pixels may get filled in below
        p = PKDict(raw_pixels=None)
        v = False
        try:
            if not (l := txn.field_get(n)):
                return None
            p.raw_pixels = numpy.load(l)
            v = True
            return p
        except Exception as e:
            pkdlog("numpy.load error={} path={} link={} stack={}", e, l, n, pkdexc())
        finally:
            txn.field_set(plot, p)
            txn.multi_set(tuple(_visibility(v)))

    def __read_db(self, txn):
        def _numpy_files():
            for k in txn.field_names():
                if l := txn.group_get(k, "links"):
                    if v := self.__numpy_file(txn, k, l):
                        yield k, v

        def _on_changes(changes):
            # TODO(robnagler) only needed for fractals
            # POSIT: same as sliclet.Base._work_ctx_write
            for k in sorted(changes.keys()):
                if f := getattr(self, f"on_change_{k}", None):
                    # TODO(robnagler) fractals only needs these
                    f(txn=txn, value=changes[k])

        def _set(db):
            for k in txn.field_names():
                # If cache (read/wrote last time) is unchanged,
                # there will be no updates. Avoids churn
                if k in db and db[k] != self.__db_cache.get(k):
                    txn.field_set(k, db[k])
                    yield k, db[k]

        if not (r := slicops.pkcli.yaml_db.read(self.name)):
            return False
        c = PKDict(_set(r)).pkupdate(_numpy_files())
        self.__db_cache = r
        _on_changes(c)
        return True

    def __write(self, txn):
        def _keys():
            for k in txn.field_names():
                g = txn.group_get(k, "ui")
                if g.get("clickable") or not g.get("writable"):
                    continue
                yield k

        # TODO(robnagler) work: maybe should happen outside lock
        self.__db_cache = PKDict((k, txn.field_get(k)) for k in _keys())
        slicops.pkcli.yaml_db.write(self.name, self.__db_cache)


CLASS = YAMLDb


class _DBWatcher(watchdog.events.FileSystemEventHandler):
    def __init__(self, paths, update_op):
        super().__init__()
        self.__update_op = update_op
        self.__paths = str(paths)
        self.__observer = watchdog.observers.polling.PollingObserver()
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
