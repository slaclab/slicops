### SlicOps: Beam Physics Control Interface

SlicOps controls particle accelerators and beamlines. The web
interface is comprised of SlicLets, componentized applications, which
allow operators to read and write EPICS controls.  The Python library
can be used standalone to control accelerators and beamlines
programmatically.

Repository: https://github.com/slaclab/slicops

Documentation: https://slicops.readthedocs.io

#### Development

This assumes you are running an environment most of the dependencies installed:

First time:


```sh
cd ~/src
mkdir -p slaclab
cd slaclab
git clone https://github.com/slaclab/slicops
cd slicops
# Remove existing install of epics
rm -rf ~/.local/epics
# Takes half hour or so depending on number of cores
make_cores=8 bash etc/epics-install.sh
pip install -e .
cd ui
npm install
```

Start the three services in separate terminal windows:


```sh
cd ~/src/slaclab/slicops
slicops epics sim-detector
slicops service ui-api
cd ui
npm start
```

With a tunneled connection, visit http://localhost:8000.

When you edit TypeScript files, npm will automatically update. The
ui-api service doesn't always update automatically so you may need to
restart manually. Just control-C and rerun the command.

#### License

License: http://github.com/slaclab/slicops/LICENSE

Copyright (c) 2024 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
