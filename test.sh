#!/bin/bash
#
# install lcls tools and run all tests
#
set -euo pipefail

_err() {
    _msg "$@"
    return 1
}

_main() {
    export EPICS_CA_ADDR_LIST=127.0.0.1
    export EPICS_CA_AUTO_ADDR_LIST=no
    export PYKERN_PKCLI_TEST_MAX_PROCS=4
    pykern ci run
}

_msg() {
    echo "$@" 1>&2
}

_main "$@"
