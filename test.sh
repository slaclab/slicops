#!/bin/bash
#
# install lcls tools and run all tests
#
set -euo pipefail

_err() {
    _msg "$@"
    return 1
}

_lcls_tools() {
    if python -c 'import lcls_tools' >& /dev/null; then
        return
    fi
    pip install scipy scikit-learn git+https://github.com/slaclab/lcls-tools
}

_main() {
    _lcls_tools
    PYKERN_PKCLI_TEST_MAX_PROCS=4 pykern ci run
}

_msg() {
    echo "$@" 1>&2
}

_main "$@"
