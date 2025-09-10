"""Plot functions

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import h5py
import numpy
import pykern.pkio
import scipy.optimize


class ImageSet:
    """Fits images, possibly averaging.

    Can take arbitrary meta data, e.g. pv and it will be written by
    `save_file`.

    Args:
        meta (PKDict): n_average, camera, curve_fit_method, pv

    """

    def __init__(self, meta):
        self.meta = meta
        self._frames = []
        self._timestamps = []
        self._prev = None

    def add_frame(self, frame, timestamp):
        """Add and update fit

        Args:
            frame (ndarray): new image
            timestamp (datetime): time of frame
        Returns:
            PKDict: frame and fit or None if not enough frames
        """

        def _mean():
            if self.meta.n_average == 1:
                return self._frames[-1]
            return numpy.mean(self._frames, axis=0)

        self._frames.append(frame)
        self._timestamps.append(timestamp)
        if len(self._frames) != self.meta.n_average:
            return None
        self._prev = PKDict(
            fit=fit_image(_mean(), self.meta.curve_fit_method),
            frames=self._frames,
            timestamps=self._timestamps,
        )
        self._frames = []
        self._timestamps = []
        return self._prev.fit

    def save_file(self, dir_path):
        # TODO(robnagler) the naming is a bit goofy, possibly frames/{images,timestamps} and analysis.
        """Creates a hdf5 file with the structure::
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
            /meta Group (camera, curve_fit_method, n_average, etc.)

        Args:
            dir_path (py.path): directory
        """

        def _image_dim(meta_group, dim):
            g = meta_group.create_group(dim)
            f = self._prev.fit[dim]
            g.create_dataset("profile", data=f.lineout)
            if not f.fit.results:
                return
            g.attrs.update(f.results)
            g.create_dataset("fit", data=f.fit.fit_line)

        def _meta(h5_file):
            g = h5_file.create_group("meta")
            g.attrs.update(self.meta)
            g.create_dataset("frames", data=self._prev.frames)
            g.create_dataset(
                "timestamps", data=(d.timestamp() for d in self._prev.timestamps)
            )

        def _path():
            # TODO(robnagler) centralize timestamp format
            t = self._prev.timestamps[-1]
            rv = dir_path.join(
                t.strftime("%Y-%m"),
                f"{t.strftime('%Y%m%d%H%M%S')}-{self.meta.camera}.h5",
            )
            rv.dirpath().ensure(dir=True)
            return rv

        def _writer(path):
            with h5py.File(path, "w") as f:
                _meta(f)
                g = f.create_group("image")
                g.dataset("mean", self._prev.fit.raw_pixels)
                _image_dim(g, "x")
                _image_dim(g, "y")

        pykern.pkio.atomic_write(_path(), writer=_writer)

    def _ready(self):
        return


def fit_image(image, method):
    """Attemp an analytical fit for the sum along the x and y dimensions

    Uses scipy.optimize.curve_fit

    Args:
        image (ndarray): 2-d matrix
        method (str): Either gaussian or  super_gaussian
    Returns:
        PKDict: raw_pixels, x & y={lineout: sum, fit: {fit_line, results: {sig, amp, mean, offset}}
    """

    def _one(profile):
        def _fix(results):
            # sigma may be negative from the fit
            results.sig = abs(results.sig)
            return results

        def _gaussian(x, amplitude, mean, sigma, offset):
            return amplitude * numpy.exp(-(((x - mean) / sigma) ** 2) / 2) + offset

        def _super_gaussian(x, amplitude, mean, sigma, offset, p):
            return amplitude * numpy.exp(-numpy.abs((x - mean) / sigma) ** p) + offset

        popt = None
        dist_keys = ["amp", "mean", "sig", "offset"]
        # TODO(pjm): should use physical camera dimensions
        x = numpy.arange(len(profile))
        try:
            m = _gaussian
            popt, pcov = scipy.optimize.curve_fit(
                m,
                x,
                profile,
                p0=[
                    numpy.mean(profile),
                    len(profile) / 2,
                    len(profile) / 5,
                    numpy.min(profile),
                ],
            )
            if method == "super_gaussian":
                # use gaussian fit to guess other distribution starting values
                m = _super_gaussian
                dist_keys.append("p")
                popt, pcov = scipy.optimize.curve_fit(
                    m, x, profile, p0=numpy.append(popt, 1.1)
                )
            elif method != "gaussian":
                raise AssertionError(f"invalid fit method={method}")
            fit_line = m(x, *popt)
        except RuntimeError as e:
            # TODO(pjm): show fitting error message on curve fit method field
            fit_line = numpy.zeros(len(x))
        return PKDict(
            lineout=profile,
            fit=PKDict(
                fit_line=fit_line,
                results=None if popt is None else _fix(PKDict(zip(dist_keys, popt))),
            ),
        )

    return PKDict(
        raw_pixels=image,
        x=_one(image.sum(axis=0)),
        y=_one(image.sum(axis=1)[::-1]),
    )
