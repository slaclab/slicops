"""Profile monitor Sliclet

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from datetime import datetime
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import h5py
import numpy
import pykern.pkconfig
import pykern.pkio
import pykern.util
import queue
import slicops.device
import slicops.device_db
import slicops.plot
import slicops.sliclet
import threading

_DEVICE_TYPE = "PROF"

_cfg = None

_BUTTONS_DISABLE = (
    ("single_button.ui.enabled", False),
    ("stop_button.ui.enabled", False),
    ("start_button.ui.enabled", False),
)

_DEVICE_DISABLE = (
    ("color_map.ui.enabled", False),
    ("color_map.ui.visible", False),
    ("curve_fit_method.ui.enabled", False),
    ("curve_fit_method.ui.visible", False),
    ("plot.ui.visible", False),
    # Useful to avoid large ctx sends
    ("plot.value", None),
    ("pv.ui.visible", False),
    ("pv.value", None),
    ("single_button.ui.visible", False),
    ("start_button.ui.visible", False),
    ("stop_button.ui.visible", False),
    ("save_button.ui.visible", False),
    ("n_average.ui.visible", False),
    ("save_button.ui.enabled", False),
) + _BUTTONS_DISABLE

_DEVICE_ENABLE = (
    ("pv.ui.visible", True),
    ("single_button.ui.visible", True),
    ("start_button.ui.visible", True),
    ("stop_button.ui.visible", True),
    ("save_button.ui.visible", True),
    ("n_average.ui.visible", True),
    ("single_button.ui.enabled", True),
    ("stop_button.ui.enabled", False),
    ("start_button.ui.enabled", True),
)

_PLOT_ENABLE = (
    ("color_map.ui.enabled", True),
    ("color_map.ui.visible", True),
    ("curve_fit_method.ui.enabled", True),
    ("curve_fit_method.ui.visible", True),
    ("plot.ui.visible", True),
)


class Screen(slicops.sliclet.Base):
    def handle_destroy(self):
        self.__device_destroy()

    def on_change_camera(self, txn, value, **kwargs):
        self.__device_change(txn, value)

    def on_change_beam_path(self, txn, value, **kwargs):
        self.__beam_path_change(txn, value)

    def on_change_curve_fit_method(self, txn, **kwargs):
        self.__update_plot(txn)

    def on_click_save_button(self, txn, **kwargs):
        self.__image.save(
            PKDict(
                [
                    (k, txn.field_get(k))
                    for k in ("pv", "camera", "curve_fit_method", "pv")
                ]
            ),
        )

    def on_click_single_button(self, txn, **kwargs):
        self.__single_button = True
        self.__set_acquire(txn, True)

    def on_click_start_button(self, txn, **kwargs):
        self.__set_acquire(txn, True)

    def on_click_stop_button(self, txn, **kwargs):
        self.__set_acquire(txn, False)

    def handle_init(self, txn):
        self.__device = None
        self.__image = _ImageSet()
        self.__monitors = PKDict()
        self.__single_button = False
        txn.multi_set(("beam_path.constraints.choices", slicops.device_db.beam_paths()))
        self.__beam_path_change(txn, None)
        self.__device_change(txn, None)
        b = c = None
        if pykern.pkconfig.in_dev_mode():
            b = _cfg.dev.beam_path
            c = _cfg.dev.camera
        # the values are None by default, but this initializes
        # the state of the choices, buttons and fields appropriately
        txn.field_set("beam_path", b)
        self.__beam_path_change(txn, b)
        txn.field_set("camera", c)

    def handle_start(self, txn):
        self.__device_setup(txn, txn.field_get("camera"))

    def __beam_path_change(self, txn, value):
        def _choices():
            if value is None:
                return ()
            return slicops.device_db.device_names(_DEVICE_TYPE, value)

        txn.multi_set(
            ("camera.constraints.choices", _choices()),
            ("camera.value", None),
        )
        # This technically shouldn't happen
        if value is None:
            txn.multi_set(
                _DEVICE_DISABLE
                + (("camera.ui.enabled", False), ("camera.ui.visible", False))
            )
        else:
            txn.multi_set((("camera.ui.enabled", True), ("camera.ui.visible", True)))
        if not self.__device:
            # No device change
            return
        c = self.__device.device_name
        if txn.is_field_value_valid("camera", c):
            # Camera is the same so restore the value, no device change
            txn.field_set("camera", c)
        else:
            self.__device_change(txn, None)

    def __device_change(self, txn, camera):
        self.__device_destroy(txn)
        txn.multi_set(_DEVICE_DISABLE)
        if camera:
            self.__device_setup(txn, camera)

    def __device_destroy(self, txn=None):
        if not self.__device:
            return
        self.__single_button = False
        for m in self.__monitors.values():
            m.destroy()
        self.__monitors = PKDict()
        try:
            n = self.__device.device_name
        except Exception:
            n = None
        try:
            self.__device.destroy()
        except Exception as e:
            pkdlog("destroy device={} error={}", n, e)
        self.__device = None

    def __device_setup(self, txn, camera):
        def _monitors():
            for n, h in (
                ("image", self.__handle_image),
                ("acquire", self.__handle_acquire),
            ):
                a = self.__device.accessor(n)
                m = self.__monitors[n] = _Monitor(a, h)
                a.monitor(m)

        try:
            # If there's an epics issues, we have to clear the device
            self.__device = self.__device = slicops.device.Device(camera)
            _monitors()
        except slicops.device.DeviceError as e:
            pkdlog("error={} setting up {}, clearing; stack={}", e, camera, pkdexc())
            self.__device_destroy(txn)
            self.__user_alert(txn, "unable to connect to camera={} error={}", camera, e)
            return
        txn.multi_set(_DEVICE_ENABLE + (("pv.value", self.__device.meta.pv_prefix),))

    def __handle_acquire(self, acquire):
        with self.lock_for_update() as txn:
            n = not acquire
            # Leave plot alone
            txn.multi_set(
                ("single_button.ui.enabled", n),
                ("start_button.ui.enabled", n),
                (
                    "stop_button.ui.enabled",
                    acquire and not self.__single_button,
                ),
            )
            if not acquire:
                self.__single_button = False

    def __handle_image(self, image):
        with self.lock_for_update() as txn:
            if (
                self.__update_plot(txn, txn.field_get("n_average"))
                and self.__single_button
            ):
                self.__set_acquire(txn, False)
                txn.multi_set(
                    ("single_button.ui.enabled", True),
                    ("start_button.ui.enabled", True),
                )

    def __set_acquire(self, txn, acquire):
        if not self.__device:
            # buttons already disabled
            return
        v = self.__monitors.acquire.prev_value()
        if v is not None and v == acquire:
            # No button disable since nothing changed
            return
        if txn:
            # No presses until we get a response from device
            txn.multi_set(_BUTTONS_DISABLE)
        try:
            self.__device.put("acquire", acquire)
        except slicops.device.DeviceError as e:
            pkdlog(
                "error={} on {}, clearing camera; stack={}", e, self.__device, pkdexc()
            )
            raise pykern.util.APIError(e)

    #    def __target_moved(self, status):
    #        if status is failed:
    #            display error
    #        if status is out:
    #            disable buttons
    #        if status is in:
    #            enable buttons
    #
    def __update_plot(self, txn, n_average=None):
        if not self.__device:
            return False
        if n_average is None:
            if not self.__image.ready():
                return False
        else:
            if (i := self.__monitors.image.prev_value()) is None or not i.size:
                return False
            # TODO(pjm): timestamp should be EPICS timestamp included with image data
            if not self.__image.add(i, datetime.now(), n_average):
                return False
        if not txn.group_get("plot", "ui", "visible"):
            txn.multi_set(_PLOT_ENABLE)
        txn.field_set("plot", self.__image.fit(txn.field_get("curve_fit_method")))
        if not txn.group_get("save_button", "ui", "enabled"):
            txn.multi_set(("save_button.ui.enabled", True))
        return True

    def __user_alert(self, txn, fmt, *args):
        pkdlog("TODO: USER ALERT: " + fmt, *args)


CLASS = Screen


class _ImageSet:
    """Collects images for averaging"""

    def __init__(self):
        self._complete = None
        self._frames = []

    def add(self, image, timestamp, n_average):
        """Add an image to the set. Returns True if ready"""
        assert n_average
        if len(self._frames) >= n_average:
            # n_average changed while collecting frames
            self._frames = self._frames[: n_average - 1]
        self._frames.append(
            PKDict(
                image=image,
                timestamp=timestamp,
            )
        )
        if len(self._frames) == n_average:
            self._complete = self._frames
            self._frames = []
            return True
        return False

    def fit(self, curve_fit_method):
        assert self.ready()
        if len(self._complete) == 1:
            i = self._complete[0].image
        else:
            i = numpy.mean(numpy.array([v.image for v in self._complete]), axis=0)
        return slicops.plot.fit_image(i, curve_fit_method)

    def ready(self):
        return bool(self._complete)

    def save(self, metadata):
        """Creates a hdf5 file with the structure:
        /image Group
          /frames Dataset {n_average, ysize, xsize}
          /mean Dataset {ysize, xsize}
          /timestamps Dataset {n_average}
          /x Group
            /fit Dataset {xsize}
            /profile Dataset {xsize}
          /y Group
            /fit Dataset {ysize}
            /profile Dataset {ysize}
        /meta Group (beam_path, camera, pv, curve_fit_method)
        """
        assert self.ready()
        i = self.fit(metadata.curve_fit_method)
        with h5py.File(self._file_path(metadata), "w") as hf:
            g = hf.create_group("meta")
            for f in metadata:
                g.attrs[f] = metadata[f]
            g = hf.create_group("image")
            g.create_dataset("mean", data=i.raw_pixels)
            for dim in ("x", "y"):
                g2 = g.create_group(dim)
                g2.create_dataset("profile", data=i[dim].lineout)
                if not i[dim].fit.results:
                    continue
                for f in i[dim].fit.results:
                    g2.attrs[f] = i[dim].fit.results[f]
                g2.create_dataset("fit", data=i[dim].fit.fit_line)
            g.create_dataset(
                "frames", data=numpy.array([v.image for v in self._complete])
            )
            g.create_dataset(
                "timestamps", data=[v.timestamp.timestamp() for v in self._complete]
            )

    def _file_path(self, metadata):
        t = self._complete[-1].timestamp
        # TODO(pjm): not sure about filename or whether it should be nested in directories
        n = f"Screen-{metadata.camera}-{t.strftime('%Y-%m-%d-%f')}.h5"
        p = pykern.pkio.py_path(_cfg.save_file_path).join(n)
        if p.exists():
            p.remove()
        return str(p)


class _Monitor:
    # TODO(robnagler) handle more values besides plot
    def __init__(self, accessor, handler):
        self.__name = str(accessor)
        self.__destroyed = False
        self.__handler = handler
        self.__value = None
        self.__change_q = queue.Queue(1)
        self.__lock = threading.Lock()
        self.__thread = threading.Thread(
            target=self.__dispatch,
            daemon=True,
            # Reduce the places where locking needs to occur
            args=(self.__name, self.__change_q, self.__lock, self.__handler),
        )
        self.__thread.start()

    def destroy(self):
        with self.__lock:
            if self.__destroyed:
                return
            self.__destroyed = True
            try:
                # if there is an exception, ignore it because the queue already has an item for wakeup dispatch
                self.__change_q.put_nowait(False)
            except Exception:
                pass
            # cause callers to crash
            try:
                delattr(self, "value")
            except Exception:
                pass

    def prev_value(self):
        with self.__lock:
            if self.__destroyed:
                return
            return self.__value

    def __call__(self, change):
        with self.__lock:
            if self.__destroyed:
                return
            if e := change.get("error"):
                pkdlog("error={} on {}", e, change.get("accessor"))
                return
            if (v := change.get("value")) is None:
                return
            try:
                self.__change_q.put_nowait(v)
            except queue.Full:
                if self.__change_q.get_nowait() is not None:
                    self.__change_q.task_done()
                # puts are locked
                self.__change_q.put_nowait(v)

    def __dispatch(self, name, change_q, lock, handler):
        try:
            while True:
                v = change_q.get()
                change_q.task_done()
                with lock:
                    if self.__destroyed:
                        return
                    self.__value = v
                try:
                    handler(v)
                except Exception as e:
                    # Touches self.__name which should not be modified
                    pkdlog("handler error={} accessor={} stack={}", e, name, pkdexc())
        except Exception as e:
            pkdlog("error={} accessor={} stack={}", e, name, pkdexc())
        finally:
            self.destroy()


def _init():
    global _cfg

    _cfg = pykern.pkconfig.init(
        dev=PKDict(
            beam_path=("DEV_BEAM_PATH", str, "dev beam path name"),
            camera=("DEV_CAMERA", str, "dev camera name"),
        ),
        save_file_path=("/tmp", str, "root path for screen save files"),
    )


_init()
