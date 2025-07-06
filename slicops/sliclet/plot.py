"""Plot functions

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import numpy
import scipy.optimize


def fit_image(self, image, fit_method):
    """Use the scipy curve_fit() to match the selected method.
       Valid methods are (gaussian, super_gaussian).
    """
    def _one(self, profile):
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
            if fit_method == "super_gaussian":
                # use gaussian fit to guess other distribution starting values
                m = _super_gaussian
                dist_keys.append("p")
                popt, pcov = scipy.optimize.curve_fit(
                    m, x, profile, p0=numpy.append(popt, 1.1)
                )
            elif fit_method != "gaussian":
                raise AssertionError(f"invalid fit method={fit_method}")
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
        raw_pixels=self.image,
        x=_one(image.sum(axis=0)),
        y=_one(image.sum(axis=1)[::-1]),
    )
