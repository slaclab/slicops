"""Test slicops.device

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

_ACCESSORS = ("acquire", "image", "target_status")


def test_target():
    from pykern.pkcollections import PKDict
    from pykern import pkdebug, pkunit
    from slicops import device_screen, unit_util
    import queue, time

    class _Handler(device_screen.EventHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.q = PKDict({k: queue.Queue() for k in _ACCESSORS + ("error",)})

        def on_screen_device_error(self, **kwargs):
            pkdebug.pkdp(kwargs)
            self.q.error.put_nowait(PKDict(kwargs))

        def on_screen_device_update(self, **kwargs):
            self.q[kwargs["accessor_name"]].put_nowait(PKDict(kwargs))

    with unit_util.start_ioc(pkunit.data_dir()):

        d = None
        h = _Handler()
        a = None
        try:
            d = device_screen.DeviceScreen("CU_HXR", "YAG03", h)
            for a in _ACCESSORS:
                h.q[a].get(timeout=2)
            d.move_target(want_in=True)
            time.sleep(3)
            assert 0
            # pkunit.pkeq(1, d.accessor("target_status").get())
            #
            # pkunit.pkeq(2, d.accessor("target_status").get())
            # d.remove_target()
            # pkunit.pkeq(1, d.accessor("target_status").get())
            # u = device_db.upstream_devices("PROF", "target_control", "CU_HXR", "YAG03")
            # pkunit.pkeq(list(u.keys()), ["YAG01", "YAG02"])
            # pkunit.pkeq(d.blocking_devices(), {"YAG01"})
            # d.unblock_upstream()
            # a = u.get("YAG01").device.accessor("target_status")
            # pkunit.pkeq(1, a.get())
            return
        except queue.Empty:
            pass
        finally:
            if d:
                d.destroy()
        pkunit.pkfail(f"timeout waiting on q.{a}")
