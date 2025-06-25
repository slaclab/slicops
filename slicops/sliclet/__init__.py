"""Base for sliclets

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import queue
import threading

_Work(enum.IntEnum):
    # sort in value order
    error=1,
    session_end=2,
    update=3,
    ui_action=4,

class Sliclet:
    def __init__(self, name, session, update_queue):
        super().__init__(daemon=True)
        self._name = name
        self._session = session
        self._update_queue = update_queue
        self._work_queue = queue.PriorityQueue()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def session_end(self):
        self._put_work(_Work.session_end, None)

    def ui_action(self, api_args):
        self._put_work(_Work.error, api_args)

    def _put_work(self, work, arg):
        self._work_queue.put_nowait(work, arg)))

    def _run(self):
        def _destroy():
            self._session = None
            self._update_queue = None
            self._work_queue = None
            self._thread = None

        try:
            while True:
                w, a = self.__work_queue.get()
                if w == _Work.session_end:
                    return
                try:
                    getattr(self, f"_work_{w._name_}")(a)
                except Exception as e:
                    pkdlog("{}={} error={} stack={}", w, a, e, pkdexc())
                    if w == _Work.error:
                        # raise SystemExit?
                        raise
                    self._put_work(_Work.error, a)
        finally:
            _destroy()


    def _work_error(self, arg):
        pass

    def _work_ui_action(self, arg):
        pass
