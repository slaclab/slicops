"""Workshop example: counting calls in API log

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

# This is here only to allow pretty printing the examples more easily.
# In tests we defer imports (put inside test functions) so import errors have correct context.
from pykern import pkunit, pkio, pkdebug
from pykern.pkcollections import PKDict
import queue
import threading
import time


import asyncio


def test_producer_consumer():
    def consumer(work):
        while i := work.get():
            print(i)

    def producer(work):
        for i in "hello", "world", None:
            time.sleep(1)
            work.put(i)

    def start():
        q = queue.Queue()
        threading.Thread(target=producer, args=(q,)).start()
        consumer(q)

    start()
