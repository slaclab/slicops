"""Front-end command line for :mod:`slicops`.

See :mod:`pykern.pkcli` for how this module is used.

:copyright: Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

import pykern.pkcli
import sys


def main():
    return pykern.pkcli.main("slicops")


if __name__ == "__main__":
    sys.exit(main())
