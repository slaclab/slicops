"""Test plot

:copyright: Copyright (c) 2025 RadiaSoft LLC.  All Rights Reserved.
:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""

from pykern import pkunit


def test_imageset_save_to_file():
    from glob import glob
    from pykern import pkio
    import h5py

    i = _imageset()
    with pkio.save_chdir(pkunit.work_dir()) as w:
        i.imageset.save_file(w)
        with h5py.File(glob("2024-09/*.h5")[0]) as h:
            pkunit.pkeq(
                h["/image/mean"][:].tolist(),
                i.expected_mean,
            )


def test_imageset_stats():
    i = _imageset()
    f = i.frame
    pkunit.pkeq(
        f.raw_pixels.tolist(),
        i.expected_mean,
    )
    pkunit.pkeq(
        f.x.lineout.tolist(),
        [0.5, 2.5, 12.5, 2.5, 0.5],
    )
    pkunit.pkeq(
        f.y.lineout.tolist(),
        [3, 5, 7.5, 3],
    )
    pkunit.pkeq(round(f.x.fit.results.sig, 2), 0.53)
    pkunit.pkeq([round(v, 2) for v in f.x.fit.fit_line], [0.5, 2.5, 12.5, 2.5, 0.5])


def _imageset():
    from datetime import datetime
    from pykern.pkcollections import PKDict
    from slicops.plot import ImageSet
    import numpy

    def _image(values):
        return numpy.array(values).reshape(4, 5)

    i = ImageSet(
        PKDict(
            images_to_average=2,
            camera="Test",
            curve_fit_method="gaussian",
            pv="test",
        )
    )
    pkunit.pkeq(
        i.add_frame(
            _image(
                [
                    0,
                    0,
                    5,
                    0,
                    0,
                    0,
                    5,
                    10,
                    0,
                    0,
                    0,
                    0,
                    5,
                    5,
                    0,
                    0,
                    0,
                    5,
                    0,
                    0,
                ]
            ),
            datetime.strptime("2024-09-19 15:45:30", "%Y-%m-%d %H:%M:%S"),
        ),
        None,
    )
    return PKDict(
        imageset=i,
        frame=i.add_frame(
            _image(
                [
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                ]
            ),
            datetime.strptime("2024-09-19 15:45:31", "%Y-%m-%d %H:%M:%S"),
        ),
        expected_mean=_image(
            [
                0.5,
                0,
                2.5,
                0,
                0,
                0,
                2.5,
                5,
                0,
                0,
                0,
                0,
                2.5,
                2.5,
                0,
                0,
                0,
                2.5,
                0,
                0.5,
            ]
        ).tolist(),
    )
