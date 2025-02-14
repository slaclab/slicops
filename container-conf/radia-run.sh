#!/bin/bash
#
# Start epics sim-detector and then the ui_api server
#
set -euo pipefail
slicops epics sim-detector --ioc-sim-detector-dir='{sim_det_dir}' &
slicops service ui_api --prod --tcp-port="${RADIA_RUN_PORT:-8080}"
