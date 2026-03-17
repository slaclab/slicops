"""Workshop example: counting calls in API log

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

# This is here only to allow pretty printing the examples more easily.
# In tests we defer imports (put inside test functions) so import errors have correct context.
from pykern import pkunit, pkio, pkdebug
from pykern.pkcollections import PKDict
import asyncio


def test_producer_consumer():
    async def consumer(work):
        while x := await work.get():
            print(x)

    async def producer(work):
        for x in "hello", "world", None:
            await asyncio.sleep(1)
            await work.put(x)

    async def start():
        x = asyncio.Queue()
        asyncio.create_task(producer(x))
        await consumer(x)

    asyncio.run(start())
