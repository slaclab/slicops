"""Fractals app

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import numpy as np
import slicops.plot
import slicops.sliclet.simple


class Fractals(slicops.sliclet.simple.Simple):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_ctx_set_mode(self, txn, value, **kwargs):
        j = value == "Julia"
        txn.multi_set(
            ("density_i.ui.visible", j),
            ("density_r.ui.visible", j),
        )

    def handle_ctx_set_save(self, txn, **kwargs):
        super().handle_ctx_set_save(txn, **kwargs)
        self.__update_plot(txn)

    def __generate_mandelbrot(self, width, height, x_min, x_max, y_min, y_max, max_iterations):
        # Create a grid of complex numbers
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)
        C = x + 1j * y[:, np.newaxis]
        Z = np.zeros_like(C, dtype=np.complex128)
        M = np.full(C.shape, max_iterations, dtype=int)
        for i in range(max_iterations):
            # Find points that haven't escaped
            mask = np.abs(Z) <= 2.0
            # Update Z for non-escaped points
            Z[mask] = Z[mask] * Z[mask] + C[mask]

            # Update escape times for newly escaped points
            escaped_mask = (np.abs(Z) > 2.0) & mask
            M[escaped_mask] = i
        return M

    def __update_plot(self, txn):
        if not txn.ui_get("plot", "visible"):
            txn.multi_set((("plot.ui.visible", True), ("color_map.ui.visible", True)))

        # Image parameters
        width, height = (800,) * 2
        x_min, x_max = -2.0, 1.0
        y_min, y_max = -1.5, 1.5
        max_iterations = 3
        # Generate the fractal
        image = self.__generate_mandelbrot(width, height, x_min, x_max, y_min, y_max, max_iterations)
        txn.field_set(
            "plot",
            PKDict(
                raw_pixels=image,
            ),
        )


CLASS = Fractals
