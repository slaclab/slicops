"""Generate fractals controlled by a simple db

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdlog, pkdp
import datetime
import numpy
import pykern.pkcli
import random
import slicops.pkcli.simple
import time

_SLICLET = "fractals"


def forever(period):
    pkdlog("database={}", path())
    if (period := int(period)) < 3:
        pykern.pkcli.command_error("period too short={}", period)
    while True:
        # TODO(robnagler) exceptions
        pkdlog("computing")
        once()
        pkdlog("sleeping")
        time.sleep(period)


def once():
    p = slicops.pkcli.simple.read(_SLICLET)
    g = _compute(p)
    rv = PKDict(plot_file=str(path()))
    if g is None:
        pykern.pkio.unchecked_remove(rv.plot_file)
        rv.message = f"invalid method={p.method}"
    else:
        numpy.save(str(rv.plot_file), g)
        rv.message = "Finished: " + datetime.datetime.utcnow().isoformat(
            timespec="seconds"
        )
    slicops.pkcli.simple.write(_SLICLET, rv)


def path():
    return slicops.pkcli.simple.path(_SLICLET).new(basename="fractals.npy")


def _compute(params):
    if params.mode == "Julia":
        return _julia(
            complex(params.density_r, params.density_i), params.size, params.iterations
        )
    if params.mode == "Mandelbrot":
        return _mandelbrot(params.size, params.iterations)
    return None


def _julia(c, num_iterations, size):
    x_min, x_max = (-1.5, 1.5)
    y_min, y_max = (-1.5, 1.5)
    # Create the complex plane grid
    real_axis = numpy.linspace(x_min, x_max, size)
    imaginary_axis = numpy.linspace(y_min, y_max, size)
    Z = real_axis[numpy.newaxis, :] + 1j * imaginary_axis[:, numpy.newaxis]

    # Initialize iteration count array
    iterations = numpy.zeros(Z.shape, dtype=int)
    # Mask for points that haven't diverged yet
    diverged = numpy.zeros(Z.shape, dtype=bool)
    random_perturbation = random.random() * 1e-3

    for i in range(num_iterations):
        # Apply the Julia set formula only to non-diverged points
        Z[~diverged] = Z[~diverged] ** 2 + c + random_perturbation

        # Check for divergence (magnitude > 2)
        current_diverged = (numpy.abs(Z) > 2) & (~diverged)
        iterations[current_diverged] = i
        diverged = diverged | current_diverged

        # Break if all points have diverged
        if numpy.all(diverged):
            break

    # Assign num_iterations to points that didn't diverge
    iterations[~diverged] = num_iterations
    return iterations


def _mandelbrot(size, iterations):
    x_min, x_max = (-2.0, 1.0)
    y_min, y_max = (-1.5, 1.5)
    # Create a grid of complex numbers
    x = numpy.linspace(x_min, x_max, size)
    y = numpy.linspace(y_min, y_max, size)
    C = x + 1j * y[:, numpy.newaxis]

    Z = numpy.zeros_like(C, dtype=numpy.complex128)
    M = numpy.full(C.shape, iterations, dtype=int)
    random_perturbation = random.random() * 1e-2

    for i in range(iterations):
        # Find points that haven't escaped
        mask = numpy.abs(Z) <= 2.0

        # Update Z for non-escaped points
        Z[mask] = (
            (1 + random_perturbation) * Z[mask] * Z[mask]
            + C[mask]
            + random_perturbation
        )

        # Update escape times for newly escaped points
        escaped_mask = (numpy.abs(Z) > 2.0) & mask
        M[escaped_mask] = i

    return M
