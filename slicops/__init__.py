""":mod:`slicops` package

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pkg_resources

try:
    # We only have a version once the package is installed.
    __version__ = pkg_resources.get_distribution("slicops").version
except pkg_resources.DistributionNotFound:
    pass
