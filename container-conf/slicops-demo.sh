#!/bin/bash
#
# Start epics sim-detector and then the ui_api server
#
set -euo pipefail
if [[ ! -w . ]]; then
    # Must be writable but likely emphemeral (needed for sim_detector.log)
    # In docker, cwd defaults to "/" so cd home
    cd
    if [[ ! -w . ]]; then
        cd /tmp
    fi
    echo "Working directory: $PWD"
fi
p=${RADIA_RUN_PORT:-8080}
slicops epics sim-detector --ioc-sim-detector-dir='{sim_det_dir}' &
# Wait for detector to start so ui_api startup message comes out after
# Match detector sleep
sleep 2
# Have message come out at the end. The ui_api starts in a second
(sleep 5; cat) <<EOF &

Point your browser to http://localhost:$p
To stop the server, type control-C here.
EOF
slicops service ui_api --prod --tcp-port="$p"
