#!/bin/bash
#
# Container startup script to print instructions
#
# Set environment, print message,
#
set -euo pipefail
export PYKERN_PKASYNCIO_SERVER_PORT=8080
cat <<'EOF'
On dev, run: slicops-demo
On prod, run: slicops service ui_api --prod
To see other commands, run: slicops
EOF
exec bash "$@"
