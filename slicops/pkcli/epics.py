"""SlicOps EPICS utilities.

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import epics
import os
import pykern.pkcli
import pykern.pkio
import subprocess
import time

# Local so should connect quickly
_SIM_DETECTOR_TIMEOUT = 5
_LOG_BASE = "sim_detector.log"


def init_sim_detector():
    """Initialize the ADSimDetector module with useful default values."""
    for name, value in {
        "13SIM1:cam1:SimMode": 1,
        "13SIM1:cam1:PeakStartX": 600,
        "13SIM1:cam1:PeakStartY": 400,
        "13SIM1:cam1:PeakNumX": 1,
        "13SIM1:cam1:PeakNumY": 2,
        "13SIM1:cam1:PeakStepX": 300,
        "13SIM1:cam1:PeakStepY": 140,
        "13SIM1:cam1:PeakWidthX": 90,
        "13SIM1:cam1:PeakWidthY": 60,
        "13SIM1:cam1:PeakVariation": 10,
        "13SIM1:cam1:Noise": 50,
        "13SIM1:cam1:Gain": 100,
        "13SIM1:cam1:AcquirePeriod": 0.5,
        "13SIM1:cam1:SizeX": 1024,
        "13SIM1:cam1:SizeY": 768,
        "13SIM1:image1:EnableCallbacks": 1,
    }.items():
        pv = epics.PV(name)
        v = pv.put(value, wait=True, timeout=_SIM_DETECTOR_TIMEOUT)
        if not pv.connected:
            raise RuntimeError(f"PV={name} failed to connect")
        if v is None:
            raise RuntimeError(f"PV={name} ")


def sim_detector(ioc_sim_detector_dir=None):
    """Run an EPICS IOC Sim Detector

    Args:
      ioc_sim_detector_dir (str, optional): Directory containing EPICS code for iocSimDetector
    """
    # TODO(robnagler) use https://github.com/ralphlange/procServ
    # Macs don't have /dev/stdin|out so /dev/tty is more portable

    def _app_path(dir_path):
        p = dir_path.join("../../bin/*/simDetectorApp")
        f = pykern.pkio.sorted_glob(p)
        if len(f) == 0:
            pykern.pkcli.command_error("no files matching pattern={}", p)
        if len(f) > 1:
            pykern.pkcli.command_error("too many simDetectorApps={}", f)
        return str(f[0])

    def _dir():
        return pykern.pkio.py_path(
            ioc_sim_detector_dir
            or "~/.local/epics/extensions/synApps/support/areaDetector-R3-12-1/ADSimDetector/iocs/simDetectorIOC/iocBoot/iocSimDetector"
        )

    def _log():
        f = pykern.pkio.py_path(_LOG_BASE)
        pkdlog("log: {}", f)
        return f.open("w+")

    def _st_cmd(dir_path):
        """POSIT: st.cmd contains `<envPaths <st_base.cmd` so we
        don't have to write a temporary file.
        """
        return dir_path.join("envPaths").read("rb") + dir_path.join("st_base.cmd").read("rb")

    d = _dir()
    with _log() as o:
        p = subprocess.Popen(
            [_app_path(d)],
            stdin=subprocess.PIPE,
            stdout=o,
            stderr=subprocess.STDOUT,
        )
    try:
        p.stdin.write(_st_cmd(d))
        p.stdin.flush()
        # do not close: input hangs, because ioc exits at EOF
        pkdlog("started pid={}; sleep 2 seconds", p.pid)
        # Wait a little bit for the process to initialize and print
        time.sleep(2)
        pkdlog("initializing sim detector")
        init_sim_detector()
        pkdlog("waiting for pid={} to exit", p.pid)
        p.wait()
    finally:
        if p.poll() is not None:
            p.terminate()
            time.sleep(1)
            p.kill()
