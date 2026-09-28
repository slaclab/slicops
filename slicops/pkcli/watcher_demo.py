"""Demo of pyepics_watcher against the slicops YAML IOC.

Starts ``slicops ioc run`` on ``package_data/watcher_demo``, reads a few
waveforms and a scalar with plain ``epics.caget()``, then starts a separate
``writer`` process that puts each PV at its own rate (see ``_PVS``) while a
PVTracker logs terse summary lines and periodic full per-PV snapshots to a
file. Shows what caget() leaves behind: a PV object in ``_PVcache_`` with a
live monitor (for arrays under ``epics.ca.AUTOMONITOR_MAXLENGTH``) and the
cached values that go with it. The writer's own CA traffic is in another
process, so it doesn't appear in the tracker's output.

:copyright: Copyright (c) 2026 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import numpy
import os
import pykern.pkio
import pykern.pkresource
import slicops.unit_util
import subprocess
import sys
import time

# DEMO:WF:LARGE is 100000 doubles; libca's default limit is 16384 bytes
_MAX_ARRAY_BYTES = "10000000"

# POSIT: count matches the initial value in watcher_demo/ioc.yaml
_PVS = PKDict(
    {
        "DEMO:WF:SMALL": PKDict(count=1000, hz=20),
        "DEMO:WF:MEDIUM": PKDict(count=20000, hz=5),
        "DEMO:WF:IMAGE": PKDict(count=3250, hz=1),
        "DEMO:WF:LARGE": PKDict(count=100000, hz=2),
        "DEMO:SCALAR": PKDict(count=1, hz=10),
    }
)


def run(log="pyepics_watcher_demo.log", seconds=20):
    """Start the demo IOC and writer, caget the PVs, and log tracker output

    Args:
        log (str): summary and snapshot output file (replaced)
        seconds (int): how long the tracker logs while the writer runs
    """
    p = pykern.pkio.py_path(log)
    pykern.pkio.unchecked_remove(p)
    with slicops.unit_util.random_epics_ports():
        # POSIT: env must be set before epics is imported (libca reads it)
        # and before the IOC and writer processes start (they inherit it)
        os.environ["EPICS_CA_MAX_ARRAY_BYTES"] = _MAX_ARRAY_BYTES
        s = _start("ioc", "run", str(pykern.pkresource.file_path("watcher_demo")))
        try:
            _demo(p, int(seconds))
        finally:
            s.terminate()
            s.wait()


def writer():
    """Put each demo PV at its rate until killed

    Started by run() as a separate process, alternating each PV between
    two values so every put is a change.
    """
    import epics

    n = time.monotonic()
    w = [
        PKDict(
            pv=epics.PV(k, auto_monitor=False),
            period=1 / v.hz,
            pair=_value_pair(v.count),
            due=n,
        )
        for k, v in _PVS.items()
    ]
    for x in w:
        if not x.pv.wait_for_connection(timeout=5):
            raise AssertionError(f"writer could not connect pv={x.pv.pvname}")
    while True:
        x = min(w, key=lambda x: x.due)
        time.sleep(max(0, x.due - time.monotonic()))
        x.pair.reverse()
        x.pv.put(x.pair[0])
        x.due += x.period


def _caget_pvs():
    import epics

    for n in _PVS:
        v = epics.caget(n, timeout=5)
        if v is None:
            raise AssertionError(f"caget failed pv={n}")
        # scalars come back as Python floats
        v = numpy.asarray(v)
        pkdlog("caget pv={} count={} bytes={}", n, v.size, v.nbytes)


def _demo(log_path, seconds):
    from slicops.pyepics_watcher import tracker

    # Before any caget so the initial gets and subscriptions are counted
    t = tracker.PVTracker(
        log_path=str(log_path),
        sample_interval_s=1.0,
        log_interval_s=1.0,
        snapshot_interval_s=5.0,
    )
    _wait_for_ioc()
    _caget_pvs()
    w = _start("watcher_demo", "writer")
    try:
        t.start()
        pkdlog("tracker logging to {} for {}s", log_path, seconds)
        try:
            time.sleep(seconds)
        finally:
            t.stop()
        if w.poll() is not None:
            raise AssertionError(f"writer exited early returncode={w.returncode}")
    finally:
        w.terminate()
        w.wait()
    pkdlog("done, see {}", log_path)


def _start(*args):
    return subprocess.Popen([sys.executable, "-m", "slicops.slicops_console", *args])


def _value_pair(count):
    if count == 1:
        return [0.0, 1.0]
    v = numpy.arange(count, dtype=float)
    return [v, v + 1]


def _wait_for_ioc():
    import epics

    n = next(iter(_PVS))
    for _ in range(10):
        if epics.caget(n, timeout=1) is not None:
            return
    raise AssertionError(f"IOC did not respond pv={n}")
