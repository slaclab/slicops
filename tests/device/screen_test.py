"""Test slicops.device

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

_ACCESSORS = ("acquire", "image", "target_status")


_TIMEOUT = 2


def test_target():
    from pykern.pkcollections import PKDict
    from pykern import pkdebug, pkunit
    from slicops import unit_util
    from slicops.device import screen
    import queue, time

    class _Handler(screen.EventHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.event_q = PKDict({k: queue.Queue() for k in _ACCESSORS + ("error",)})

        def on_screen_device_error(self, **kwargs):
            pkdebug.pkdp(kwargs)
            self.event_q.error.put_nowait(PKDict(kwargs))

        def on_screen_device_update(self, **kwargs):
            self.event_q[kwargs["accessor_name"]].put_nowait(PKDict(kwargs))

        def test_get(self, event_name):
            try:
                return self.event_q[event_name].get(timeout=_TIMEOUT).value
            except queue.Empty:
                pkunit.pkfail("timeout event={}", event_name)

    with unit_util.start_ioc(pkunit.data_dir()):
        h = _Handler()
        d = screen.Screen("CU_HXR", "YAG03", h)
        try:
            h.test_get("image")
            pkunit.pkeq(False, h.test_get("acquire"))
            pkunit.pkeq(False, h.test_get("target_status"))
            d.move_target(want_in=True)
            pkunit.pkeq(True, h.test_get("target_status"))
            d.move_target(want_in=False)
            pkunit.pkeq(False, h.test_get("target_status"))
            # d.unblock_upstream()
            # a = u.get("YAG01").device.accessor("target_status")
            # pkunit.pkeq(1, a.get())
        finally:
            d.destroy()
